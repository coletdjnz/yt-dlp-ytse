import base64
import dataclasses
import enum
import time
import protobug
from yt_dlp import traverse_obj, int_or_none, DownloadError
from yt_dlp.downloader import FileDownloader
from yt_dlp.extractor.youtube import INNERTUBE_CLIENTS
from yt_dlp.networking import Request
from yt_dlp_plugins.extractor._ytse.protos import ClientAbrState, VideoPlaybackAbrRequest, PlaybackCookie, MediaHeader, StreamProtectionStatus, SabrRedirect, FormatInitializationMetadata, NextRequestPolicy, LiveMetadata, SabrSeek, SabrError
from yt_dlp_plugins.extractor._ytse.protos._buffered_range import BufferedRange
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos._streamer_context import StreamerContext, ClientInfo
from yt_dlp_plugins.extractor._ytse.ump import UMPParser, UMPPart, UMPPartType


class FormatType(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'


def get_format_key(format_id: FormatId):
    return f'{format_id.itag}-{format_id.last_modified}'


@dataclasses.dataclass
class SABRFormat:
    itag: int
    last_modified_at: int
    format_type: FormatType
    quality: str
    height: str
    write_callback: callable


@dataclasses.dataclass
class Sequence:
    format_id: FormatId
    is_init_segment: bool = False
    duration_ms: int = 0
    start_ms: int = 0
    start_data_range: int = 0
    sequence_number: int = 0
    content_length: int = 0


@dataclasses.dataclass
class InitializedFormat:
    format_id: FormatId
    video_id: str
    buffered_range: BufferedRange
    requested_format: SABRFormat
    total_duration_ms: int = 0
    end_time_ms: int = 0
    current_content_length: int = 0
    current_duration_ms: int = 0
    mime_type: str = None
    sequences: dict[int, Sequence] = dataclasses.field(default_factory=dict)


class SABRStream:
    def __init__(self, fd, server_abr_streaming_url: str, video_playback_ustreamer_config: str, po_token_fn: callable, formats: list[SABRFormat], client_info: ClientInfo):
        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token_fn = po_token_fn
        self.requestedFormats = formats
        self.client_info = client_info

        self.client_abr_state: ClientAbrState = None

        self.next_request_policy: NextRequestPolicy = None

        self.initialized_formats: dict[str, InitializedFormat] = {}
        self.header_id_to_format_map: dict[int, str] = {}
        self.live_metadata: LiveMetadata = None

        self.fd: FileDownloader = fd

        self.total_duration_ms = None

    def download(self):
        video_formats = [format for format in self.requestedFormats if format.format_type == FormatType.VIDEO]
        audio_formats = [format for format in self.requestedFormats if format.format_type == FormatType.AUDIO]

        # note: MEDIA_TYPE_VIDEO is no longer supported
        media_type = ClientAbrState.MediaType.MEDIA_TYPE_DEFAULT
        if len(video_formats) == 0:
            media_type = ClientAbrState.MediaType.MEDIA_TYPE_AUDIO

        selected_audio_format_ids = [FormatId(itag=format.itag, last_modified=format.last_modified_at) for format in audio_formats]
        selected_video_format_ids = [FormatId(itag=format.itag, last_modified=format.last_modified_at) for format in video_formats]

        # initialize client abr state
        self.client_abr_state = ClientAbrState(
            last_manual_direction=0,
           time_since_last_manual_format_selection_ms=0,
           visibility=0,
           start_time_ms=0, # todo
            #quality="720",

           media_type=media_type,
        )

        request_number = 0
        # add a small buffer to account for small difference in format length
        while self.live_metadata or not self.total_duration_ms or self.client_abr_state.start_time_ms + 100 < self.total_duration_ms:
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
                buffered_ranges=[initialized_format.buffered_range for initialized_format in self.initialized_formats.values()],
            )
            payload = protobug.dumps(vpabr)

            self.fd.write_debug(f'Requested video playback abr request. {vpabr}')

            response = self.fd.ydl.urlopen(
                Request(
                    url=self.server_abr_streaming_url,
                    method='POST',
                    data=payload,
                    query={'rn': request_number},
                )
            )

            self.parse_ump_response(response)

            ivs = list(self.initialized_formats.values())

            format_min_duration = ivs and min(self.initialized_formats.values(), key=lambda x: x.current_duration_ms)

            # next request policy backoff_time_ms is the minimum to increment start_time_ms by
            self.client_abr_state.start_time_ms = max(
                (format_min_duration and format_min_duration.current_duration_ms) or 0,
                self.client_abr_state.start_time_ms + ((self.next_request_policy and self.next_request_policy.backoff_time_ms) or 0),
                self.client_abr_state.start_time_ms + 1000
            )

            if len(self.header_id_to_format_map):
                self.fd.report_warning('Extraneous header IDs left')
                self.header_id_to_format_map.clear()

            if self.live_metadata and self.client_abr_state.start_time_ms >= self.total_duration_ms:
                self.client_abr_state.start_time_ms = self.total_duration_ms
                wait_time = ((self.next_request_policy and self.next_request_policy.backoff_time_ms) or 0) or (self.live_metadata.target_duration_sec * 1000 * 2)
                self.fd.write_debug(f'sleeping {wait_time / 1000} seconds')
                time.sleep(wait_time / 1000)

            self.next_request_policy = None

            request_number += 1

            self.fd.write_debug(f'{self.client_abr_state.start_time_ms}/{self.total_duration_ms}')

        for initialized_format in self.initialized_formats.values():
            initialized_format.requested_format.write_callback(b'', close=True)

    def write_ump_debug(self, part, message):
        #if traverse_obj(self.ydl.params, ('extractor_args', 'youtube', 'ump_debug', 0, {int_or_none}), get_all=False) == 1:
        self.fd.write_debug(f'[{part.part_type.name}]: (Size {part.size}) {message}')

    def write_ump_warning(self, part, message):
        self.fd.report_warning(f'[{part.part_type.name}]: (Size {part.size}) {message}')

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

        # duration_ms may not be provided - instead time_range is given (ios)
        duration_ms = (
                media_header.duration_ms
                or (media_header.time_range and int((media_header.time_range.duration / media_header.time_range.timescale) * 1000))
                or 0)
        if self.live_metadata and not duration_ms:
            duration_ms = self.live_metadata.target_duration_sec * 1000



        initialized_format.sequences[sequence_number or 0] = Sequence(
            format_id=media_header.format_id,
            is_init_segment=is_init_segment,
            duration_ms=duration_ms,
            start_data_range=media_header.start_data_range,
            sequence_number=sequence_number,
            content_length=media_header.content_length,
            start_ms=media_header.start_ms,
        )

        self.header_id_to_format_map[media_header.header_id] = get_format_key(media_header.format_id)

        if not is_init_segment and sequence_number != 0:

            if initialized_format.buffered_range.end_segment_index + 1 != sequence_number:
                self.write_ump_warning(part, f'End segment index mismatch: {initialized_format.buffered_range.end_segment_index + 1} != {sequence_number}. Jumping to {sequence_number}.')

            initialized_format.buffered_range.end_segment_index = sequence_number
            initialized_format.buffered_range.duration_ms += duration_ms

        content_length = media_header.content_length
        if content_length:
            initialized_format.current_content_length = content_length
        initialized_format.current_duration_ms += duration_ms or 0

    def process_media(self, part: UMPPart):
        header_id = part.data[0]
        self.write_ump_debug(part, f'Header ID: {header_id}')

        format_key = self.header_id_to_format_map.get(header_id)
        if not format_key:
            self.write_ump_warning(part, f'Initialized Format not found for header ID {header_id}')
            return

        initialized_format = self.initialized_formats.get(format_key)

        if not initialized_format:
            self.write_ump_warning(part, f'Initialized Format not found for header ID {header_id}')
            return

   #     self.write_ump_debug(part, f'Writing {len(part.data[1:])} bytes to initialized format {initialized_format}')

        # todo: improve write callback
        write_callback = initialized_format.requested_format.write_callback
        write_callback(part.data[1:])

    def process_media_end(self, part: UMPPart):
        header_id = part.data[0]
        self.write_ump_debug(part, f' Header ID: {header_id}')
        self.header_id_to_format_map.pop(header_id, None)

    def process_live_metadata(self, part: UMPPart):
        self.live_metadata = protobug.loads(part.data, LiveMetadata)
        self.write_ump_debug(part, f'Live Metadata: {self.live_metadata} Data: {part.get_b64_str()}')
        if self.live_metadata.latest_sequence_duration_ms:
            self.total_duration_ms = self.live_metadata.latest_sequence_duration_ms

    def process_stream_protection_status(self, part: UMPPart):
        sps = protobug.loads(part.data, StreamProtectionStatus)
        self.write_ump_debug(part, f'Status: {StreamProtectionStatus.Status(sps.status).name} Data: {part.get_b64_str()}')
        if sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
            self.fd.report_error('StreamProtectionStatus: Attestation Required (missing PO Token?)')

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

    def process_format_initialization_metadata(self, part: UMPPart):
        fmt_init_metadata = protobug.loads(part.data, FormatInitializationMetadata)
        self.write_ump_debug(part, f'Format Initialization Metadata: {fmt_init_metadata} Data: {part.get_b64_str()}')

        initialized_format_key = get_format_key(fmt_init_metadata.format_id)

        if initialized_format_key in self.initialized_formats:
            self.fd.report_warning('Format already initialized')
            return
        # find matching requested format key

        matching_requested_format = next((format for format in self.requestedFormats if get_format_key(FormatId(itag=format.itag, last_modified=format.last_modified_at) ) == initialized_format_key), None)

        if not matching_requested_format:
            self.write_ump_warning(part, f'Format {initialized_format_key} not in requested formats.. Ignoring')
            return

        initialized_format = InitializedFormat(
            format_id=fmt_init_metadata.format_id,
            total_duration_ms=int((fmt_init_metadata.duration / fmt_init_metadata.duration_timescale) * 1000),
            end_time_ms=fmt_init_metadata.end_time_ms,
            mime_type=fmt_init_metadata.mime_type,
            buffered_range=BufferedRange(
                format_id=fmt_init_metadata.format_id,
                start_time_ms=0,
                duration_ms=0,
                start_segment_index=0,
                end_segment_index=0,
                # todo: also use time range for ios? perhaps will avoid duplicate segments..
            ),
            video_id=fmt_init_metadata.video_id,
            requested_format=matching_requested_format,
        )
         # fmt total_duration_ms may be inaccurate - end_time_ms is usually accurate though? (ios)
        self.total_duration_ms = max(self.total_duration_ms or 0, fmt_init_metadata.end_time_ms or 0)

        self.initialized_formats[get_format_key(fmt_init_metadata.format_id)] = initialized_format

        self.write_ump_debug(part, f'Initialized Format: {initialized_format}')\


    def process_next_request_policy(self, part: UMPPart):
        self.next_request_policy = protobug.loads(part.data, NextRequestPolicy)
        self.write_ump_debug(part, f'Next Request Policy: {self.next_request_policy} Data: {part.get_b64_str()}')

    def process_sabr_seek(self, part: UMPPart):
        sabr_seek = protobug.loads(part.data, SabrSeek)
        seek_to = (sabr_seek.start / sabr_seek.timescale) * 1000
        self.write_ump_debug(part, f'Sabr Seek: {sabr_seek} Data: {part.get_b64_str()}')
        self.write_ump_debug(part, f'Seeking to {seek_to}ms')

        for initialized_format in self.initialized_formats.values():
            initialized_format.buffered_range.start_time_ms = int(seek_to)
            initialized_format.buffered_range.duration_ms = 0
            initialized_format.current_content_length = 0
            initialized_format.current_duration_ms = int(seek_to)
            initialized_format.sequences.clear()

    def process_sabr_error(self, part: UMPPart):
        sabr_error = protobug.loads(part.data, SabrError)
        self.fd.report_error(f'SABR Error: {sabr_error} Data: {part.get_b64_str()}')


class SABRFD(FileDownloader):

    @classmethod
    def can_download(cls, info_dict):
        # todo: validate all formats

        return (
            info_dict.get('requested_formats') and
            all(format_info.get('protocol') == 'sabr' for format_info in info_dict['requested_formats'])
        )

    def real_download(self, filename, info_dict):

        # todo: Here we would sort formats into groups of audio + video, and per client

        # assuming we have only selected audio + video, and they are of the same client, for now.

        requested_formats = info_dict['requested_formats']

        formats = []
        po_token_fn = lambda: None
        server_abr_streaming_url = None
        video_playback_ustreamer_config = None
        client_name = None
        innertube_context = None
        def create_write_callback(format):
            stream = None
            tmpfilename = self.temp_name(format.get('filepath'))
            open_mode = 'wb'
            try:
                stream, tmpfilename = self.sanitize_open(
                tmpfilename, open_mode)
                assert stream is not None
                filename = self.undo_temp_name(tmpfilename)
                self.report_destination(filename)
            except OSError as err:
                self.report_error(f'unable to open for writing: {err}')
                return False

            def callback(data, close=False):
                if close:
                    self.write_debug(f'Closing {filename}')
                    stream.close()
                    return True
                self.write_debug(f'Writing {len(data)} bytes to {filename}')
                try:
                    stream.write(data)
                except OSError as err:
                    self.to_stderr('\n')
                    self.report_error(f'unable to write data: {err}')
                    return False

            return callback


        for format in requested_formats:
            sabr_config = format.get('_sabr_config')

            if not server_abr_streaming_url:
                server_abr_streaming_url = format.get('url')

            if server_abr_streaming_url != format.get('url'):
                self.report_error('All formats must have the same server_abr_streaming_url')
                return

            if not video_playback_ustreamer_config:
                video_playback_ustreamer_config = sabr_config.get('video_playback_ustreamer_config')

            if video_playback_ustreamer_config != sabr_config.get('video_playback_ustreamer_config'):
                self.report_error('All formats must have the same video_playback_ustreamer_config')
                return

            if not client_name:
                client_name = sabr_config.get('client_name')

            if client_name != sabr_config.get('client_name'):
                self.report_error('All formats must have the same client_name')
                return

            if not innertube_context:
                innertube_context = sabr_config.get('innertube_context')

            po_token = sabr_config.get('po_token')
            if po_token:
                po_token_fn = lambda: po_token


            formats.append(SABRFormat(
                itag = int(sabr_config['itag']),
                last_modified_at = int_or_none(sabr_config.get('last_modified')),
                format_type = FormatType.VIDEO if format.get('acodec') == 'none' else FormatType.AUDIO,
                quality=None,
                height=None,
                write_callback=create_write_callback(format)
            ))

        innertube_client = INNERTUBE_CLIENTS.get(client_name)
        client_info = ClientInfo(
            client_name = innertube_client['INNERTUBE_CONTEXT_CLIENT_NAME'],
            client_version= traverse_obj(innertube_client, ('INNERTUBE_CONTEXT', 'client', 'clientVersion')),
        )

        stream = SABRStream(self, server_abr_streaming_url, video_playback_ustreamer_config, po_token_fn, formats, client_info)
        stream.download()

        for format in requested_formats:
            filename = format.get('filepath')
            self.try_rename(self.temp_name(filename), filename)

        return True
