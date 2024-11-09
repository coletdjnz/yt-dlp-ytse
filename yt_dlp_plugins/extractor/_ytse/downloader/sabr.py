import base64
import collections
import dataclasses
import enum
import itertools
import math
import time
import typing
from typing import List
import protobug
from yt_dlp import traverse_obj, int_or_none, DownloadError
from yt_dlp.downloader import FileDownloader
from yt_dlp.extractor.youtube import INNERTUBE_CLIENTS
from yt_dlp.networking import Request
from yt_dlp.utils.progress import ProgressCalculator
from yt_dlp_plugins.extractor._ytse.protos import ClientAbrState, VideoPlaybackAbrRequest, PlaybackCookie, MediaHeader, StreamProtectionStatus, SabrRedirect, FormatInitializationMetadata, NextRequestPolicy, LiveMetadata, SabrSeek, SabrError
from yt_dlp_plugins.extractor._ytse.protos._buffered_range import BufferedRange
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos._streamer_context import StreamerContext, ClientInfo
from yt_dlp_plugins.extractor._ytse.protos._time_range import TimeRange
from yt_dlp_plugins.extractor._ytse.ump import UMPParser, UMPPart, UMPPartType


class FormatType(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'


def get_format_key(format_id: FormatId):
    return f'{format_id.itag}-{format_id.last_modified}-{format_id.xtags}'


@dataclasses.dataclass
class SABRStatus:
    start_bytes: int = 0
    fragment_index: int = None
    fragment_count: int = None


@dataclasses.dataclass
class FormatRequest:
    format_type: FormatType
    format_id: FormatId
    write_callback: typing.Callable[[bytes, SABRStatus], None]
    quality: typing.Optional[str] = None
    height: typing.Optional[str] = None


@dataclasses.dataclass
class Sequence:
    format_id: FormatId
    is_init_segment: bool = False
    duration_ms: int = 0
    start_ms: int = 0
    start_data_range: int = 0
    sequence_number: int = 0
    content_length: int = 0
    initialized_format: 'InitializedFormat' = None


@dataclasses.dataclass
class InitializedFormat:
    format_id: FormatId
    video_id: str
    requested_format: FormatRequest
    duration_ms: int = 0
    end_time_ms: int = 0
    mime_type: str = None
    sequences: dict[int, Sequence] = dataclasses.field(default_factory=dict)
    buffered_ranges: List[BufferedRange] = dataclasses.field(default_factory=list)


class SABRStream:
    def __init__(self, fd, server_abr_streaming_url: str, video_playback_ustreamer_config: str, po_token_fn: callable, client_info: ClientInfo, video_formats: List[FormatRequest] = None, audio_formats: List[FormatRequest] = None, live_segment_target_duration_sec: int = 5):

        self._requested_video_formats: List[FormatRequest] = video_formats or []
        self._requested_audio_formats: List[FormatRequest] = audio_formats or []
        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token_fn = po_token_fn
        self.client_info = client_info
        self.client_abr_state: ClientAbrState = None
        self.next_request_policy: NextRequestPolicy = None
        self.initialized_formats: dict[str, InitializedFormat] = {}
        self.header_ids: dict[int, Sequence] = {}
        self.live_metadata: LiveMetadata = None
        self.fd: FileDownloader = fd
        self.total_duration_ms = None
        self.sabr_seeked = False
        self.live_segment_target_duration_sec = live_segment_target_duration_sec
        self._request_had_data = False

    def download(self):
        # note: MEDIA_TYPE_VIDEO is no longer supported
        media_type = ClientAbrState.MediaType.MEDIA_TYPE_DEFAULT
        if len(self._requested_video_formats) == 0:
            media_type = ClientAbrState.MediaType.MEDIA_TYPE_AUDIO

        # todo: handle non-format-id format requests
        selected_audio_format_ids = [f.format_id for f in self._requested_audio_formats]
        selected_video_format_ids = [f.format_id for f in self._requested_video_formats]

        self._requested_format_ids = selected_audio_format_ids + selected_video_format_ids

        # initialize client abr state
        self.client_abr_state = ClientAbrState(
            start_time_ms=0,  # current duration
            media_type=media_type,
        )

        requests_no_data = 0

        request_number = 0
        while self.live_metadata or not self.total_duration_ms or self.client_abr_state.start_time_ms < self.total_duration_ms:
            po_token = self.po_token_fn()
            vpabr = VideoPlaybackAbrRequest(
                client_abr_state=self.client_abr_state,
                selected_video_format_ids=selected_video_format_ids,
                selected_audio_format_ids=selected_audio_format_ids,
                selected_format_ids=[
                    initialized_format.format_id for initialized_format in self.initialized_formats.values()
                ],
                video_playback_ustreamer_config=base64.urlsafe_b64decode(self.video_playback_ustreamer_config),
                streamer_context=StreamerContext(
                     po_token=po_token and base64.urlsafe_b64decode(po_token),
                     playback_cookie=self.next_request_policy and protobug.dumps(self.next_request_policy.playback_cookie),
                     client_info=self.client_info
                 ),
                buffered_ranges=[
                    buffered_range for initialized_format in self.initialized_formats.values()
                    for buffered_range in initialized_format.buffered_ranges
                ],
            )
            payload = protobug.dumps(vpabr)

            self.fd.write_debug(f'Requested video playback abr request. {vpabr}')

            response = self.fd.ydl.urlopen(
                Request(
                    url=self.server_abr_streaming_url,
                    method='POST',
                    data=payload,
                    query={'rn': request_number},
                    headers={'content-type': 'application/x-protobuf'}
                )
            )

            self.parse_ump_response(response)

            if len(self.header_ids):
                self.fd.report_warning('Extraneous header IDs left')
                self.header_ids.clear()

            if not self._request_had_data:
                if requests_no_data >= 2:
                    if self.client_abr_state.start_time_ms < self.total_duration_ms:
                        raise DownloadError('No data found in three consecutive requests')
                    break  # stream finished?
                requests_no_data += 1

            current_buffered_ranges = [initialized_format.buffered_ranges[-1] for initialized_format in self.initialized_formats.values() if initialized_format.buffered_ranges]

            # choose format that is the most behind
            lowest_buffered_range = min(current_buffered_ranges, key=lambda x: x.start_time_ms + x.duration_ms) if current_buffered_ranges else None

            min_buffered_duration_ms = lowest_buffered_range.start_time_ms + lowest_buffered_range.duration_ms if lowest_buffered_range else 0

            next_request_backoff_ms = (self.next_request_policy and self.next_request_policy.backoff_time_ms) or 0

            self.client_abr_state.start_time_ms = max(
                min_buffered_duration_ms,
                # next request policy backoff_time_ms is the minimum to increment start_time_ms by
                self.client_abr_state.start_time_ms + next_request_backoff_ms,
            )

            if self.live_metadata and self.client_abr_state.start_time_ms >= self.total_duration_ms:
                self.client_abr_state.start_time_ms = self.total_duration_ms
                wait_time = next_request_backoff_ms + self.live_segment_target_duration_sec * 1000
                self.fd.write_debug(f'sleeping {wait_time / 1000} seconds')
                time.sleep(wait_time / 1000)

            self.next_request_policy = None
            self.sabr_seeked = False
            self._request_had_data = False

            request_number += 1

          #  self.fd.write_debug(f'Progress: {self.client_abr_state.start_time_ms}/{self.total_duration_ms}')

            # The response should automatically close when all data is read, but just in case...
            if not response.closed:
                response.close()

    def write_ump_debug(self, part, message):
        pass
        #if traverse_obj(self.ydl.params, ('extractor_args', 'youtube', 'ump_debug', 0, {int_or_none}), get_all=False) == 1:
        self.fd.write_debug(f'[{part.part_type.name}]: (Size {part.size}) {message}')

    def write_ump_warning(self, part, message):
        pass
        self.fd.write_debug(f'[{part.part_type.name}]: (Size {part.size}) {message}')

    def parse_ump_response(self, response):
        ump = UMPParser(response)
        for part in ump.iter_parts():
            if part.part_type == UMPPartType.MEDIA_HEADER:
                self.process_media_header(part)
            elif part.part_type == UMPPartType.MEDIA:
                self.process_media(part)
            elif part.part_type == UMPPartType.MEDIA_END:
                self.process_media_end(part)
            elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                self.process_stream_protection_status(part)
            elif part.part_type == UMPPartType.SABR_REDIRECT:
                self.process_sabr_redirect(part)
            elif part.part_type == UMPPartType.FORMAT_INITIALIZATION_METADATA:
                self.process_format_initialization_metadata(part)
            elif part.part_type == UMPPartType.NEXT_REQUEST_POLICY:
                self.process_next_request_policy(part)
            elif part.part_type == UMPPartType.LIVE_METADATA:
                self.process_live_metadata(part)
            elif part.part_type == UMPPartType.SABR_SEEK:
                self.process_sabr_seek(part)
            elif part.part_type == UMPPartType.SABR_ERROR:
                self.process_sabr_error(part)
            elif part.part_type == UMPPartType.SELECTABLE_FORMATS:
                self.process_selectable_formats(part)
            else:
                self.write_ump_warning(part, f'Unhandled part type: {part.part_type.name}:{part.part_id} Data: {part.get_b64_str()}')
                continue

    def process_media_header(self, part: UMPPart):
        media_header = protobug.loads(part.data, MediaHeader)
        self.write_ump_debug(part, f'Parsed header: {media_header} Data: {part.get_b64_str()}')
        if not media_header.format_id:
            self.write_ump_warning(part, 'Format ID not found')
            return
        initialized_format = self.initialized_formats.get(get_format_key(media_header.format_id))
        if not initialized_format:
            self.write_ump_warning(part, f'Initialized format not found for {media_header.format_id}')
            return

        sequence_number = media_header.sequence_number
        if (sequence_number or 0) in initialized_format.sequences:
            self.write_ump_warning(part, f'Sequence {sequence_number} already found, skipping')
            return

        is_init_segment = media_header.is_init_segment

        time_range = media_header.time_range

        # Calculate duration of this segment
        # For videos, either duration_ms or time_range should be present
        # For live streams, calculate segment duration based on live metadata target segment duration


        start_ms = media_header.start_ms or (time_range and time_range.get_start_ms()) or 0

        duration_ms = (
            media_header.duration_ms
            or (time_range and time_range.get_duration_ms())
            or self.live_metadata and self.live_segment_target_duration_sec * 1000
            or 0)

        initialized_format.sequences[sequence_number or 0] = Sequence(
            format_id=media_header.format_id,
            is_init_segment=is_init_segment,
            duration_ms=duration_ms,
            start_data_range=media_header.start_data_range,
            sequence_number=sequence_number,
            content_length=media_header.content_length,
            start_ms=start_ms,
            initialized_format=initialized_format
        )

        self.header_ids[media_header.header_id] = initialized_format.sequences[sequence_number or 0]

        if not is_init_segment:
            current_buffered_range = initialized_format.buffered_ranges[-1] if initialized_format.buffered_ranges else None

            # todo: if we sabr seek, then we get two segments in same request, we end up creating two buffered ranges.
            # Perhaps we should have sabr_seeked as part of initialized_format?
            if not current_buffered_range or self.sabr_seeked:
                initialized_format.buffered_ranges.append(BufferedRange(
                    format_id=media_header.format_id,
                    start_time_ms=start_ms,
                    duration_ms=duration_ms,
                    start_segment_index=sequence_number,
                    end_segment_index=sequence_number,
                    time_range=TimeRange(
                        start=start_ms,
                        duration=duration_ms,
                        timescale=1000  # ms
                    )
                ))
                self.write_ump_debug(part, f'Created new buffered range for {media_header.format_id} (sabr seeked={self.sabr_seeked}): {initialized_format.buffered_ranges[-1]}')
                return

            end_segment_index = current_buffered_range.end_segment_index or 0
            if end_segment_index != 0 and end_segment_index + 1 != sequence_number:
                raise DownloadError(f'End segment index mismatch: {end_segment_index + 1} != {sequence_number}. Buffered Range: {current_buffered_range}')

            current_buffered_range.end_segment_index = sequence_number

            if not self.live_metadata:
                # We need to increment both duration_ms and time_range.duration
                current_buffered_range.duration_ms += duration_ms
                current_buffered_range.time_range.duration += duration_ms
            else:
                # Attempt to keep in sync with livestream, as the segment duration target is not always perfect.
                # The server seems to care more about the segment index than the duration.
                if current_buffered_range.start_time_ms > start_ms:
                    raise DownloadError(f'Buffered range start time mismatch: {current_buffered_range.start_time_ms} > {start_ms}')
                new_duration = (start_ms - current_buffered_range.start_time_ms) + duration_ms
                current_buffered_range.duration_ms = current_buffered_range.time_range.duration = new_duration

    def process_media(self, part: UMPPart):
        header_id = part.data[0]
        # self.write_ump_debug(part, f'Header ID: {header_id}')

        current_sequence = self.header_ids.get(header_id)

        if not current_sequence:
            self.write_ump_warning(part, f'Header ID {header_id} not found')
            return

        initialized_format = current_sequence.initialized_format

        if not initialized_format:
            self.write_ump_warning(part, f'Initialized Format not found for header ID {header_id}')
            return

   #     self.write_ump_debug(part, f'Writing {len(part.data[1:])} bytes to initialized format {initialized_format}')

        # todo: improve write callback
        write_callback = initialized_format.requested_format.write_callback
        write_callback(part.data[1:], SABRStatus(fragment_index=current_sequence.sequence_number, fragment_count=self.live_metadata and self.live_metadata.latest_sequence_number))
        self._request_had_data = True

    def process_media_end(self, part: UMPPart):
        header_id = part.data[0]
        self.write_ump_debug(part, f' Header ID: {header_id}')
        self.header_ids.pop(header_id, None)

    def process_live_metadata(self, part: UMPPart):
        self.live_metadata = protobug.loads(part.data, LiveMetadata)
        self.write_ump_debug(part, f'Live Metadata: {self.live_metadata} Data: {part.get_b64_str()}')
        if self.live_metadata.latest_sequence_duration_ms:
            self.total_duration_ms = self.live_metadata.latest_sequence_duration_ms

    def process_stream_protection_status(self, part: UMPPart):
        sps = protobug.loads(part.data, StreamProtectionStatus)
        self.write_ump_debug(part, f'Status: {StreamProtectionStatus.Status(sps.status).name} Data: {part.get_b64_str()}')
        if sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
            raise DownloadError('StreamProtectionStatus: Attestation Required (missing PO Token?)')

    def process_sabr_redirect(self, part: UMPPart):
        sabr_redirect = protobug.loads(part.data, SabrRedirect)
        self.server_abr_streaming_url = sabr_redirect.redirect_url
        self.write_ump_debug(part, f'New URL: {self.server_abr_streaming_url}')

        # todo: validate redirect URL
        if not self.server_abr_streaming_url:
            self.fd.report_error('SABRRedirect: Invalid redirect URL')

    def process_selectable_formats(self, part: UMPPart):
        # shown on IOS. Shows available formats. Probably not very useful?
        self.write_ump_debug(part, f'Selectable Formats: {part.get_b64_str()}')

    def _find_matching_requested_format(self, format_init_metadata: FormatInitializationMetadata):
        for requested_format in self._requested_audio_formats + self._requested_video_formats:
            if requested_format.format_id:
                if requested_format.format_id == format_init_metadata.format_id:
                    return requested_format
            else:
                # todo: add more matching criteria if the requested format does not have a format_id
                pass

    def process_format_initialization_metadata(self, part: UMPPart):
        fmt_init_metadata = protobug.loads(part.data, FormatInitializationMetadata)
        self.write_ump_debug(part, f'Format Initialization Metadata: {fmt_init_metadata} Data: {part.get_b64_str()}')

        initialized_format_key = get_format_key(fmt_init_metadata.format_id)

        if initialized_format_key in self.initialized_formats:
            self.write_ump_debug(part, 'Format already initialized')
            return

        matching_requested_format = self._find_matching_requested_format(fmt_init_metadata)

        if not matching_requested_format:
            self.write_ump_warning(part, f'Format {initialized_format_key} not in requested formats.. Ignoring')
            return

        duration_ms = fmt_init_metadata.duration and math.ceil((fmt_init_metadata.duration / fmt_init_metadata.duration_timescale) * 1000)

        initialized_format = InitializedFormat(
            format_id=fmt_init_metadata.format_id,
            duration_ms=duration_ms,
            end_time_ms=fmt_init_metadata.end_time_ms,
            mime_type=fmt_init_metadata.mime_type,
            video_id=fmt_init_metadata.video_id,
            requested_format=matching_requested_format,
        )
        self.total_duration_ms = max(self.total_duration_ms or 0, fmt_init_metadata.end_time_ms or 0, duration_ms or 0)

        self.initialized_formats[get_format_key(fmt_init_metadata.format_id)] = initialized_format

        self.write_ump_debug(part, f'Initialized Format: {initialized_format}')

    def process_next_request_policy(self, part: UMPPart):
        self.next_request_policy = protobug.loads(part.data, NextRequestPolicy)
        self.write_ump_debug(part, f'Next Request Policy: {self.next_request_policy} Data: {part.get_b64_str()}')

    def process_sabr_seek(self, part: UMPPart):
        sabr_seek = protobug.loads(part.data, SabrSeek)
        seek_to = math.ceil((sabr_seek.start / sabr_seek.timescale) * 1000)
        self.write_ump_debug(part, f'Sabr Seek: {sabr_seek} Data: {part.get_b64_str()}')
        self.write_ump_debug(part, f'Seeking to {seek_to}ms')

        self.client_abr_state.start_time_ms = seek_to
        self.sabr_seeked = True

    def process_sabr_error(self, part: UMPPart):
        sabr_error = protobug.loads(part.data, SabrError)
        raise DownloadError(f'SABR Error: {sabr_error} Data: {part.get_b64_str()}')


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

    def _open(self):
        self._tmp_filename = self.fd.temp_name(self.filename)
        try:
            self.fp, self._tmp_filename = self.fd.sanitize_open(self._tmp_filename, self._open_mode)
            assert self.fp is not None
            self.filename = self.fd.undo_temp_name(self._tmp_filename)
            self.fd.report_destination(self.filename)
        except OSError as err:
            raise DownloadError(f'unable to open for writing: {err}')

    def write(self, data: bytes, metadata: SABRStatus):
        if not self._progress:
            self._progress = ProgressCalculator(metadata.start_bytes)

        if not self.fp:
            self._open()
        if self.fp.closed:
            raise ValueError('File is closed')
        self.fp.write(data)

        self._downloaded_bytes += len(data)
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
            'fragment_count': metadata.fragment_count,
            'fragment_index': metadata.fragment_index,
        }
        self.fd._hook_progress(self._state, self.info_dict)

    def finish(self):
        self._state['status'] = 'finished'
        self.fd._hook_progress(self._state, self.info_dict)
        if self.fp:
            self.fp.close()
            self.fd.try_rename(self._tmp_filename, self.filename)


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

        for idx, f in enumerate(requested_formats):
            sabr_config = f.get('_sabr_config')
            client_name = sabr_config.get('client_name')

            # Group formats by client
            # sabr_format_groups = { client_name: { server_abr_streaming_url: xyz, formats: [] } } }

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
                    # todo: pass this information down from YoutubeIE
                    'client_info': ClientInfo(
                        client_name=innertube_client['INNERTUBE_CONTEXT_CLIENT_NAME'],
                        client_version=traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'clientVersion')),
                    ),
                    'writers': []
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
                'format_id': itag and FormatId(itag=itag, last_modified=int_or_none(sabr_config.get('last_modified')), xtags=sabr_config.get('xtags')),
                'format_type': FormatType.VIDEO if f.get('acodec') == 'none' else FormatType.AUDIO,
                'quality': sabr_config.get('quality'),
                'height': sabr_config.get('height'),
                'filename': f.get('filepath', filename),
                'info_dict': f,
            })

        for name, format_group in sabr_format_groups.items():
            formats = format_group['formats']

            self.write_debug(f'Downloading formats for client {name}')

            # Group formats into video_audio pairs. SABR can currently download video+audio or audio.
            # Just video requires the audio stream to be discarded.
            audio_formats = (f for f in formats if f['format_type'] == FormatType.AUDIO)
            video_formats = (f for f in formats if f['format_type'] == FormatType.VIDEO)
            for audio_format, video_format in itertools.zip_longest(audio_formats, video_formats):
                audio_format_writer = audio_format and SABRFDWriter(self, audio_format.get('filename'), audio_format['info_dict'], 0)
                video_format_writer = video_format and SABRFDWriter(self, video_format.get('filename'), video_format['info_dict'], 1 if audio_format else 0)
                if not audio_format and video_format:
                    self.write_debug('Downloading a video stream without audio. SABR does not allow video-only, so an additional audio stream will be downloaded but discarded.')

                stream = SABRStream(
                    fd=self,
                    server_abr_streaming_url=format_group['server_abr_streaming_url'],
                    video_playback_ustreamer_config=format_group['video_playback_ustreamer_config'],
                    po_token_fn=format_group['po_token_fn'],
                    video_formats=video_format and [FormatRequest(
                        format_id=video_format['format_id'],
                        format_type=FormatType.VIDEO,
                        quality=video_format['quality'],
                        height=video_format['height'],
                        write_callback=video_format_writer.write
                    )],
                    audio_formats=audio_format and [FormatRequest(
                        format_id=audio_format['format_id'],
                        format_type=FormatType.AUDIO,
                        quality=audio_format['quality'],
                        height=audio_format['height'],
                        write_callback=audio_format_writer.write
                    )],
                    client_info=format_group['client_info']
                )
                self._prepare_multiline_status(int(bool(audio_format and video_format)) + 1)

                try:
                    stream.download()
                except KeyboardInterrupt:
                    if not info_dict.get('is_live'):
                        raise
                    self.to_screen(f'Interrupted by user')
                    return True
                finally:
                    if audio_format_writer:
                        audio_format_writer.finish()
                    if video_format_writer:
                        video_format_writer.finish()

        return True
