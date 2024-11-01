import base64
import dataclasses
import enum
import protobug
from yt_dlp import traverse_obj
from yt_dlp.downloader import FileDownloader
from yt_dlp.networking import Request
from yt_dlp_plugins.extractor._ytse.protos import ClientAbrState, VideoPlaybackAbrRequest, PlaybackCookie, MediaHeader, StreamProtectionStatus, SabrRedirect
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos._streamer_context import StreamerContext, ClientInfo
from yt_dlp_plugins.extractor._ytse.ump import UMPParser, UMPPart, UMPPartType



class FormatType(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'

@dataclasses.dataclass
class SABRFormat:
    itag: int
    last_modified_at: int
    format_type: FormatType
    quality: str
    height: str
    write_callback: callable

class SABRStream:
    def __init__(self, fd, server_abr_streaming_url: str, video_playback_ustreamer_config: str, po_token_fn: callable, formats: list[SABRFormat], client_info: ClientInfo):
        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token_fn = po_token_fn
        self.requestedFormats = formats
        self.client_info = client_info

        self.client_abr_state: ClientAbrState = None

        self.playback_cookie: PlaybackCookie = None

        self.fd: FileDownloader = fd

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
            media_type=media_type,
        )

        while True:
            vpabr = VideoPlaybackAbrRequest(
                client_abr_state=self.client_abr_state,
                selected_video_format_ids=selected_video_format_ids,
                selected_audio_format_ids=selected_audio_format_ids,
                # selected_format_ids
                video_playabck_ustreamer_config=base64.b64decode(self.video_playback_ustreamer_config),
                streamer_context = StreamerContext(
                    po_token= base64.b64decode(self.po_token_fn()),
                    playback_cookie = protobug.dumps(self.playback_cookie),
                    client_info = self.client_info
                ),
                buffered_ranges = [],
            )
            payload = protobug.dumps(vpabr)

            response = self.fd.ydl.urlopen(
                Request(
                    url = self.server_abr_streaming_url,
                    method='POST',
                    data=payload,
                )
            )

    def write_ump_debug(self, part, message):
        #if traverse_obj(self.ydl.params, ('extractor_args', 'youtube', 'ump_debug', 0, {int_or_none}), get_all=False) == 1:
        self.fd.write_debug(f'[{part.part_type.name}]: (Size {part.size}) {message}')

    def write_ump_warning(self, part, message):
        self.fd.report_warning(f'[{part.part_type.name}]: (Size {part.size}) {message}')

    def parse_ump_response(self, response):
        ump = UMPParser(response)
        for part in ump.iter_parts():
            if part.part_type == UMPPartType.MEDIA_HEADER:
                media_header = protobug.loads(part.data, MediaHeader)
                self.write_ump_debug(part, f'Parsed header: {media_header} Data: {part.get_b64_str()}')
                continue

            elif part.part_type == UMPPartType.MEDIA_END:
                self.write_ump_debug(part, f' Header ID: {part.data[0]}')
                break
            elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                sps = protobug.loads(part.data, StreamProtectionStatus)
                self.write_ump_debug(part, f'Status: {StreamProtectionStatus.Status(sps.status).name} Data: {part.get_b64_str()}')
                if sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
                    response.close()
                    self.report_error('StreamProtectionStatus: Attestation Required (missing PO Token?)')
                    return False

            elif part.part_type == UMPPartType.SABR_REDIRECT:
                sabr_redirect = protobug.loads(part.data, SabrRedirect)
                self.server_abr_streaming_url = sabr_redirect.redirect_url
                self.write_ump_debug(part, f'New URL: {self.server_abr_streaming_url}')
                if not self.server_abr_streaming_url:
                    response.close()
                    self.report_error('SABRRedirect: Invalid redirect URL')
                    return False




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

        for format in requested_formats:
            pass


