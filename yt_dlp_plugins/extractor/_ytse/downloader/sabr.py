from __future__ import annotations
import collections
import dataclasses
import itertools
import os
import typing
import protobug
from yt_dlp.downloader import FileDownloader
from yt_dlp.networking.exceptions import TransportError, HTTPError

try:
    from yt_dlp.extractor.youtube._base import INNERTUBE_CLIENTS
except ImportError:
    from yt_dlp.extractor.youtube import INNERTUBE_CLIENTS

from yt_dlp.utils import traverse_obj, int_or_none, DownloadError
from yt_dlp.utils._utils import _YDLLogger
from yt_dlp.utils.progress import ProgressCalculator

from ..protos.videostreaming.format_id import FormatId
from ..protos.videostreaming.buffered_range import BufferedRange
from ..protos.innertube.client_info import ClientInfo

from ..sabr import SabrStream, AudioSelector, VideoSelector, MediaSegmentSabrPart, PoTokenStatusSabrPart, \
    RefreshPlayerResponseSabrPart, MediaSeekSabrPart, FormatInitializedSabrPart


@dataclasses.dataclass
class SABRStatus:
    start_bytes: int = 0
    fragment_index: int = None
    fragment_count: int = None


@protobug.message
class SabrSegment:
    sequence_number: protobug.Int32 = protobug.field(1)
    content_length: protobug.Int64 = protobug.field(3)


@protobug.message
class SabrSequence:
    sequence_start_number: protobug.Int32 = protobug.field(2)
    sequence_filename: protobug.String = protobug.field(3)
    segments: list[SabrSegment] = protobug.field(4)

@protobug.message
class SabrInitSegment:
    filename: protobug.String = protobug.field(1)
    content_length: protobug.Int64 = protobug.field(2)

# protobug class that we will save to a file to track the current downloaded progress of a sabr format
@protobug.message
class SabrProgressDocument:
    format_id: FormatId = protobug.field(1)
    buffered_ranges: list[BufferedRange] = protobug.field(2, default_factory=list)
    init_segment: typing.Optional[SabrInitSegment] = protobug.field(3, default=None)
    sequences: list[SabrSequence] = protobug.field(4, default_factory=list)

    # xxx: rewrite this crap
    def find_sequence(self, sequence_number):
        for sequence in self.sequences:
            if sequence.sequence_start_number > sequence_number:
                continue
            sorted_segments = sorted(sequence.segments, key=lambda s: s.sequence_number)
            if not sorted_segments:
                raise Exception('Corrupt sequence')
            last_segment = sorted_segments[-1]
            if last_segment == sequence_number:
                raise Exception('Segment already downloaded')

            if last_segment.sequence_number == sequence_number - 1:
                return sequence

        return None


class SABRFDWriter:
    def __init__(self, fd, filename, infodict, progress_idx=0):
        self.fd = fd
        self.fp = None
        self.filename = filename
        self._tmp_filename = None
        self._open_mode = 'wb'
        self._progress = None
        self.info_dict = infodict
        self._downloaded_bytes = 0
        self.progress_idx = progress_idx
        self._state = {}
        self._sequence_fps: dict[str, tuple[str, typing.Any]] = {}
        self._progress_document_file = SabrProgressFile(filename=self._sabr_document_filename, fd=fd)
        self._format_id = None

    # operation to get current buffered ranges, etc.

    @property
    def _sabr_document_filename(self):
        return self.filename + '.sabr.binpb'

    def _sabr_sequence_filename(self, start_sequence_number):
        # todo: probably should make these relative to the current filename so the temp files can be moved around
        return self.filename + f'.seq{start_sequence_number}.sabr.part'

    def _open(self):
        self._tmp_filename = self.fd.temp_name(self.filename)
        try:
            self.fp, self._tmp_filename = self.fd.sanitize_open(self._tmp_filename, self._open_mode)
            assert self.fp is not None
            self.filename = self.fd.undo_temp_name(self._tmp_filename)
            self.fd.report_destination(self.filename)
        except OSError as err:
            raise DownloadError(f'unable to open for writing: {err}')

    def _sequence_file(self, sequence_id, sequence_filename):
        # todo: validate the file length matches the expected length from all the segments
        # This may happen if download was interrupted before the file could completely save?
        # Attempt to recover by calculating what segment had a partial save (probably the last one)
        # We will need to sync this up with the progress document before we update the buffered ranges of the stream
        if sequence_id not in self._sequence_fps:
            try:
                fp, real_sequence_filename = self.fd.sanitize_open(sequence_filename, 'ab')
                self._sequence_fps[sequence_id] = (real_sequence_filename, fp)
                self.fd.report_destination(sequence_filename)  # tmp
            except OSError as err:
                raise DownloadError(f'unable to open for writing: {err}')
        return self._sequence_fps[sequence_id][1]

    def initialize_format(self, format_id):
        if self._format_id and self._format_id != format_id:
            raise Exception('Bad format id')
        self._format_id = format_id

    @property
    def initialized(self):
        return self._format_id is not None

    def get_progress_document(self):
        if not self._progress_document_file.exists:
            progress_document = SabrProgressDocument(
                format_id=self._format_id,
            )
        else:
            progress_document = self._progress_document_file.retrieve()

        assert progress_document.format_id == self._format_id, 'Format ID mismatch'

        return progress_document

    def close(self):
        if self.fp and not self.fp.closed:
            self.fp.close()
            self.fp = None

        for _, fp in self._sequence_fps.values():
            if not fp.closed:
                fp.close()

        self._sequence_fps.clear()


    def write(self, part: MediaSegmentSabrPart):
        if not self._progress:
            self._progress = ProgressCalculator(part.start_bytes)

        # todo: should be called before sending data
        self.initialize_format(part.format_id)

        progress_document = self.get_progress_document()
        # todo: this should merge with the existing buffered ranges
        progress_document.buffered_ranges = part.buffered_ranges
        content_length = len(part.data)

        data_filename = None
        sequence_id = None
        if not part.is_init_segment:
            segment = SabrSegment(
                sequence_number=part.sequence_number,
                content_length=content_length,
            )
            # TODO: we should limit sequence size
            # TODO: we should perhaps store sequence information in another file, so we don't have to keep editing the main one
            #  Sometimes if the file gets too large it can become easy to corrupt on shutdown
            sequence = progress_document.find_sequence(part.sequence_number)
            if not sequence:
                sequence = SabrSequence(
                    sequence_start_number=part.sequence_number,
                    sequence_filename=self._sabr_sequence_filename(part.sequence_number),
                    segments=[segment],
                )
                progress_document.sequences.append(sequence)
            else:
                sequence.segments.append(segment)

            data_filename = sequence.sequence_filename
            sequence_id = sequence.sequence_start_number
        else:
            if progress_document.init_segment:
                raise Exception('Init segment already downloaded')
            sequence_id = 'init'
            data_filename = self._sabr_sequence_filename(sequence_id)
            progress_document.init_segment = SabrInitSegment(
                filename=data_filename,
                content_length=content_length,
            )

        self._progress_document_file.update(progress_document)

        fp = self._sequence_file(sequence_id, data_filename)
        if fp.closed:
            raise ValueError('File is closed')
        fp.write(part.data)

        # calculate total downloaded bytes from all segments in all sequences
        self._downloaded_bytes = sum(
            sum(segment.content_length for segment in sequence.segments)
            for sequence in progress_document.sequences
        ) + (progress_document.init_segment.content_length if progress_document.init_segment else 0)

        self._progress.total = self.info_dict.get('filesize')
        self._progress.update(self._downloaded_bytes)
        self._state = {
            'status': 'downloading',
            'downloaded_bytes': self._downloaded_bytes,
            'total_bytes': self.info_dict.get('filesize'),
            'tmpfilename': self._tmp_filename,
            'filename': self.filename,
            'eta': self._progress.eta.smooth,
            'speed': self._progress.speed.smooth,
            'elapsed': self._progress.elapsed,
            'progress_idx': self.progress_idx,
            'fragment_count': part.fragment_count,
            'fragment_index': part.sequence_number,
        }
        self.fd._hook_progress(self._state, self.info_dict)

    def finish(self):
        self._state['status'] = 'finished'
        self.fd._hook_progress(self._state, self.info_dict)
        for _, fp in self._sequence_fps.values():
            if not fp.closed:
                fp.close()

        self._sequence_fps.clear()

        # Now merge all the sequences together

        progress_document = self.get_progress_document()

        # Open temporary file for writing
        self._open()
        sequence_filenames = []
        # May not always be an init segment, e.g for live streams
        if progress_document.init_segment:
            init_segment_fp, init_segment_filename = self.fd.sanitize_open(progress_document.init_segment.filename, 'rb')
            # Write the init segment if it exists
            self.fp.write(init_segment_fp.read())
            init_segment_fp.close()
            sequence_filenames.append(init_segment_filename)

        # Write the segments
        for sequence in sorted(progress_document.sequences, key=lambda s: s.sequence_start_number):
            sequence_fp, sequence_filename = self.fd.sanitize_open(sequence.sequence_filename, 'rb')
            sequence_filenames.append(sequence_filename)
            self.fp.write(sequence_fp.read())
            sequence_fp.close()

        # Close the temporary file
        self.fp.close()

        self.fd.try_rename(self._tmp_filename, self.filename)

        # Remove the progress document
        self._progress_document_file.remove()

        # Remove sequence files
        for sequence_filename in sequence_filenames:
            self.fd.try_remove(sequence_filename)

class SabrProgressFile:

    def __init__(self, filename, fd):
        self.filename = filename
        self.fd = fd

    # todo: handling for corrupt file
    @property
    def exists(self):
        return os.path.isfile(self.filename)

    def retrieve(self):
        stream, _ = self.fd.sanitize_open(self.filename, 'rb')
        try:
            return protobug.loads(stream.read(), SabrProgressDocument)
        finally:
            stream.close()

    def update(self, sabr_document):
        stream, _ = self.fd.sanitize_open(self.filename, 'wb')
        try:
            stream.write(protobug.dumps(sabr_document))
            return True
        finally:
            stream.close()

    def remove(self):
        self.fd.try_remove(self.filename)

class SABRFD(FileDownloader):

    @classmethod
    def can_download(cls, info_dict):
        return (
            info_dict.get('requested_formats') and
            all(format_info.get('protocol') == 'sabr' for format_info in info_dict['requested_formats'])
        )

    def real_download(self, filename, info_dict):
        requested_formats = info_dict.get('requested_formats') or [info_dict]
        sabr_format_groups = collections.defaultdict(dict, {})
        is_test = self.params.get('test', False)
        for idx, f in enumerate(requested_formats):
            sabr_config = f.get('_sabr_config')
            client_name = sabr_config.get('client_name')
            server_abr_streaming_url = f.get('url')
            video_playback_ustreamer_config = sabr_config.get('video_playback_ustreamer_config')

            if not video_playback_ustreamer_config:
                self.report_error('Video playback ustreamer config not found')
                return

            sabr_format_group_config = sabr_format_groups.get(client_name)

            if not sabr_format_group_config:
                po_token = sabr_config.get('po_token')
                innertube_client = INNERTUBE_CLIENTS.get(client_name)
                sabr_format_group_config = sabr_format_groups[client_name] = {
                    'server_abr_streaming_url': server_abr_streaming_url,
                    'video_playback_ustreamer_config': video_playback_ustreamer_config,
                    'formats': [],
                    'po_token_fn': lambda: po_token,
                    'reload_config_fn': sabr_config.get('reload_config_fn'),
                    # todo: pass this information down from YoutubeIE
                    'client_info': ClientInfo(
                        client_name=innertube_client['INNERTUBE_CONTEXT_CLIENT_NAME'],
                        client_version=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'clientVersion')),
                        os_version=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'osVersion')),
                        os_name=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'osName')),
                        device_model=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'deviceModel')),
                        device_make=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'deviceMake')),
                    ),
                    'writers': [],
                    # Number.MAX_SAFE_INTEGER
                    'start_time_ms': ((2**53) - 1) if info_dict.get('live_status') == 'is_live' and not f.get('is_from_start') else 0,
                }

            else:
                if sabr_format_group_config['server_abr_streaming_url'] != server_abr_streaming_url:
                    self.report_error('Server ABR streaming URL mismatch')
                    return

                if sabr_format_group_config['video_playback_ustreamer_config'] != video_playback_ustreamer_config:
                    self.report_error('Video playback ustreamer config mismatch')
                    return

            itag = int_or_none(sabr_config.get('itag'))
            sabr_format_group_config['formats'].append({
                'format_id': itag and FormatId(itag=itag, lmt=int_or_none(sabr_config.get('last_modified')), xtags=sabr_config.get('xtags')),
                'format_type': 'video' if f.get('acodec') == 'none' else 'audio',
                'quality': sabr_config.get('quality'),
                'height': sabr_config.get('height'),
                'filename': f.get('filepath', filename),
                'info_dict': f,
                'target_duration_sec': sabr_config.get('target_duration_sec'),
            })

        for name, format_group in sabr_format_groups.items():
            formats = format_group['formats']

            self.write_debug(f'Downloading formats for client {name}')

            # Group formats into video_audio pairs. SABR can currently download video+audio or audio.
            # Just video requires the audio stream to be discarded.
            audio_formats = (f for f in formats if f['format_type'] == 'audio')
            video_formats = (f for f in formats if f['format_type'] == 'video')
            for audio_format, video_format in itertools.zip_longest(audio_formats, video_formats):
                audio_format_writer = audio_format and SABRFDWriter(self, audio_format.get('filename'), audio_format['info_dict'], 0)
                video_format_writer = video_format and SABRFDWriter(self, video_format.get('filename'), video_format['info_dict'], 1 if audio_format else 0)
                if not audio_format and video_format:
                    self.write_debug('Downloading a video stream without audio. SABR does not allow video-only, so an additional audio stream will be downloaded but discarded.')

                video_format_request = VideoSelector(
                        format_ids=[video_format['format_id']],
                    ) if video_format else None

                audio_format_request = AudioSelector(
                        format_ids=[audio_format['format_id']],
                    ) if audio_format else None
                stream = SabrStream(
                    urlopen=self.ydl.urlopen,
                    logger=_YDLLogger(self.ydl),
                    debug=bool(traverse_obj(self.ydl.params, ('extractor_args', 'youtube', 'sabr_debug', 0, {int_or_none}), get_all=False)),
                    server_abr_streaming_url=format_group['server_abr_streaming_url'],
                    video_playback_ustreamer_config=format_group['video_playback_ustreamer_config'],
                    po_token=format_group['po_token_fn'](),
                    video_selection=video_format_request,
                    audio_selection=audio_format_request,
                    start_time_ms=format_group['start_time_ms'],
                    client_info=format_group['client_info'],
                    live_segment_target_duration_sec=format_group.get('target_duration_sec'),  # todo: should this be with the format request?
                )
                self._prepare_multiline_status(int(bool(audio_format and video_format)) + 1)

                try:
                    total_bytes = 0
                    for part in stream:
                        if is_test and total_bytes >= self._TEST_FILE_SIZE:
                            stream.close()
                            break
                        if isinstance(part, PoTokenStatusSabrPart):
                            # TODO: implement once PO Token Provider PR is merged
                            if part.status in (
                                part.PoTokenStatus.INVALID,
                                part.PoTokenStatus.PENDING,
                            ):
                                # Fetch a PO token with bypass_cache=True
                                # (ensure we create a new one)
                                pass
                            elif part.status in (
                                part.PoTokenStatus.MISSING,
                                part.PoTokenStatus.PENDING_MISSING
                            ):
                                # Fetch a PO Token, bypass_cache=False
                                pass

                        elif isinstance(part, FormatInitializedSabrPart):

                            writer = None
                            if audio_format_request and part.format_selector is audio_format_request:
                                writer = audio_format_writer
                            elif video_format_request and part.format_selector is video_format_request:
                                writer = video_format_writer
                            else:
                                self.report_warning(f'Unknown format selector: {part.format_selector}')
                                continue

                            writer.initialize_format(part.format_id)

                            self.write_debug(f'Format {part.format_id} initialized')

                            # Attempt a resume if a progress document exists for this format
                            # It is safe to update the buffered ranges at this point
                            if self.params.get('continuedl', True):
                                # todo: handle progress documents existing and ignoring them if continuedl is False
                                progress_document = writer.get_progress_document()
                                initialized_format = stream.initialized_formats[str(part.format_id)]
                                if progress_document.init_segment:
                                    initialized_format.init_segment = True
                                    initialized_format.current_segment = None  # allow a seek
                                if progress_document.buffered_ranges:
                                    initialized_format.buffered_ranges = progress_document.buffered_ranges
                                    initialized_format.current_segment = None  # allow a seek


                                self.to_screen(f'[download] Resuming download for format {part.format_id} with {len(progress_document.buffered_ranges)} buffered ranges')

                            else:
                                self.to_screen('[download] Ignoring progress document because continuedl is False')
                        elif isinstance(part, MediaSegmentSabrPart):
                            total_bytes += len(part.data)
                            if audio_format_request and part.format_selector is audio_format_request:
                                audio_format_writer.write(part)
                            elif video_format_request and part.format_selector is video_format_request:
                                video_format_writer.write(part)
                            else:
                                self.report_warning(f'Unknown format selector: {part.format_selector}')

                        elif isinstance(part, RefreshPlayerResponseSabrPart):
                            self.to_screen(f'Refreshing player response; Reason: {part.reason}')
                            # In-place refresh - not ideal but should work in most cases
                            # todo: handle case where live stream changes to non-livestream on refresh
                            if not format_group['reload_config_fn']:
                                raise self.report_warning(
                                    'No reload config function found - cannot refresh SABR streaming URL.'
                                    ' The url will expire soon and the download will fail.')
                            try:
                                stream.server_abr_streaming_url, stream.video_playback_ustreamer_config = format_group['reload_config_fn']()
                            except (TransportError, HTTPError) as e:
                                self.report_warning(f'Failed to refresh SABR streaming URL: {e}')

                        elif isinstance(part, MediaSeekSabrPart):
                            # xxx: on the fence whether this should be in SabrStream or up to the caller
                            if (
                                not info_dict.get('is_live')
                                and MediaSeekSabrPart.reason == MediaSeekSabrPart.Reason.SERVER_SEEK
                            ):
                                raise DownloadError('Server tried to seek a video')
                        else:
                            self.to_screen(f'Unhandled part type: {part}')


                    if audio_format_writer:
                        audio_format_writer.finish()
                    if video_format_writer:
                        video_format_writer.finish()

                except KeyboardInterrupt:
                    if not info_dict.get('is_live'):
                        raise
                    self.to_screen(f'Interrupted by user')
                    if audio_format_writer:
                        audio_format_writer.finish()
                    if video_format_writer:
                        video_format_writer.finish()
                finally:
                    if audio_format_writer:
                        audio_format_writer.close()
                    if video_format_writer:
                        video_format_writer.close()


        return True
