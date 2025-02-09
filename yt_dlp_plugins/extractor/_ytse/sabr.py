import base64
import dataclasses
import enum
import math
import time
import typing
from typing import List
from urllib.parse import urlparse

import protobug
from yt_dlp import DownloadError, int_or_none, traverse_obj
from yt_dlp.networking import Request, Response
from yt_dlp.networking.exceptions import HTTPError, TransportError
from yt_dlp.utils import parse_qs, update_url_query
from yt_dlp.utils._utils import _YDLLogger

from .protos import (
    ClientInfo,
    ClientAbrState,
    NextRequestPolicy,
    LiveMetadata,
    VideoPlaybackAbrRequest,
    StreamerContext,
    unknown_fields,
    MediaHeader,
    BufferedRange,
    TimeRange,
    StreamProtectionStatus,
    SabrRedirect,
    FormatInitializationMetadata,
    SabrSeek,
    SabrError,
    FormatId
)
from .ump import UMPParser, UMPPartType, UMPPart


@dataclasses.dataclass
class SABRStatus:
    start_bytes: int = 0
    fragment_index: int = None
    fragment_count: int = None


class FormatType(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'


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


def get_format_key(format_id: FormatId):
    return f'{format_id.itag}-{format_id.last_modified}-{format_id.xtags}'


class SABRStream:
    def __init__(
        self,
        urlopen: typing.Callable[[Request], Response],
        logger: _YDLLogger,
        server_abr_streaming_url: str,
        video_playback_ustreamer_config: str,
        po_token_fn: typing.Callable[[], str],
        client_info: ClientInfo,
        video_formats: List[FormatRequest] = None, audio_formats: List[FormatRequest] = None,
        live_segment_target_duration_sec: int = None,
        reload_config_fn: typing.Callable[[], tuple[str, str]] = None,
        start_time_ms: int = 0,
        debug=False,
    ):

        self._logger = logger
        self._debug = debug
        self._urlopen = urlopen
        self._requested_video_formats: List[FormatRequest] = video_formats or []
        self._requested_audio_formats: List[FormatRequest] = audio_formats or []
        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token_fn = po_token_fn
        self.reload_config_fn = reload_config_fn
        self.client_info = client_info
        self.client_abr_state: ClientAbrState = None
        self.next_request_policy: NextRequestPolicy = None
        self.initialized_formats: dict[str, InitializedFormat] = {}
        self.header_ids: dict[int, Sequence] = {}
        self.live_metadata: LiveMetadata = None
        self.total_duration_ms = None
        self.sabr_seeked = False
        self.live_segment_target_duration_sec = live_segment_target_duration_sec or 5
        self._request_had_data = False
        self._bad_hosts = []
        self._redirected = False
        self._start_time_ms = start_time_ms

    def download(self):
        # note: video only is not supported
        enabled_track_types_bitfield = 0  # Both
        if len(self._requested_video_formats) == 0:
            enabled_track_types_bitfield = 1  # Audio only

        # todo: handle non-format-id format requests
        selectable_audio_format_ids = [f.format_id for f in self._requested_audio_formats]
        selectable_video_format_ids = [f.format_id for f in self._requested_video_formats]

        self.write_sabr_debug(f'starting at: {self._start_time_ms}')
        # initialize client abr state
        self.client_abr_state = ClientAbrState(
            player_time_ms=self._start_time_ms,
            enabled_track_types_bitfield=enabled_track_types_bitfield,
        )

        if self.live_segment_target_duration_sec:
            self.write_sabr_debug(f'using live_segment_target_duration_sec: {self.live_segment_target_duration_sec}')

        requests_no_data = 0
        request_number = 0

        while self.live_metadata or not self.total_duration_ms or self.client_abr_state.player_time_ms < self.total_duration_ms:
            self._check_expiry()
            po_token = self.po_token_fn()
            vpabr = VideoPlaybackAbrRequest(
                client_abr_state=self.client_abr_state,
                selectable_video_format_ids=selectable_video_format_ids,
                selectable_audio_format_ids=selectable_audio_format_ids,
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
            self.write_sabr_debug(f'video_playback_ustreamer_config: {self.video_playback_ustreamer_config}')
            self.write_sabr_debug(f'Sending videoplayback SABR request: {vpabr}')

            # todo: add retry logic for network errors
            # For livestreams, if exceed retries, assume end of stream

            try:
                response = self._urlopen(
                    Request(
                        url=self.server_abr_streaming_url,
                        method='POST',
                        data=payload,
                        query={'rn': request_number},
                        headers={'content-type': 'application/x-protobuf'}
                    )
                )

            except HTTPError as e:
                self._logger.debug(f'HTTP Error: {e.status} - {e.reason}')

                # on 5xx errors, if a retry does not work, try falling back to another host?
                # todo: add retry logic for 5xx errors
                if 500 <= e.status < 600:
                    self.process_player_fallback()
                    continue

                raise DownloadError(f'HTTP Error: {e.status} - {e.reason}')

            except TransportError as e:
                self._logger.warning(f'Transport Error: {e}')
                self.process_player_fallback()
                continue

            try:
                self.parse_ump_response(response)
            except TransportError as e:
                # Response read errors
                self._logger.warning(f'Transport Error: {e}')
                self.process_player_fallback()

            if len(self.header_ids):
                self._logger.warning(f'Extraneous header IDs left: {list(self.header_ids.values())}')
                self.header_ids.clear()

            if not self._request_had_data:
                if requests_no_data >= 2 and not self._redirected:  # todo: how to prevent youtube sending us in a redirect loop?
                    if self.total_duration_ms and self.client_abr_state.player_time_ms < self.total_duration_ms:
                        self._logger.warning('No data found in three consecutive requests - assuming end of video')
                    break  # stream finished?
                requests_no_data += 1
            else:
                requests_no_data = 0

            current_buffered_ranges = [initialized_format.buffered_ranges[-1] for initialized_format in self.initialized_formats.values() if initialized_format.buffered_ranges]

            # choose format that is the most behind
            lowest_buffered_range = min(current_buffered_ranges, key=lambda x: x.start_time_ms + x.duration_ms) if current_buffered_ranges else None

            min_buffered_duration_ms = lowest_buffered_range.start_time_ms + lowest_buffered_range.duration_ms if lowest_buffered_range else 0

            next_request_backoff_ms = (self.next_request_policy and self.next_request_policy.backoff_time_ms) or 0

            self.client_abr_state.player_time_ms = max(
                min_buffered_duration_ms,
                # next request policy backoff_time_ms is the minimum to increment player_time_ms by
                self.client_abr_state.player_time_ms + next_request_backoff_ms,
            )

            if self.live_metadata and self.total_duration_ms and self.client_abr_state.player_time_ms >= self.total_duration_ms:
                self.client_abr_state.player_time_ms = self.total_duration_ms
                wait_time = next_request_backoff_ms + self.live_segment_target_duration_sec * 1000
                self.write_sabr_debug(f'sleeping {wait_time / 1000} seconds')
                time.sleep(wait_time / 1000)

            self.next_request_policy = None
            self.sabr_seeked = False
            self._request_had_data = False
            self._redirected = False

            request_number += 1

            # The response should automatically close when all data is read, but just in case...
            if not response.closed:
                response.close()

    def write_sabr_debug(self, message=None, part=None, protobug_obj=None, data=None):
        msg = ''
        if part:
            msg = f'[{part.part_type.name}]: (Size {part.size})'
        if protobug_obj:
            msg += f' Parsed: {protobug_obj}'
            uf = list(unknown_fields(protobug_obj))
            if uf:
                msg += f' (Unknown fields: {uf})'
        if message:
            msg += f' {message}'
        if data:
            msg += f' Data: {base64.b64encode(data).decode("utf-8")}'
        if self._debug:
            self._logger.debug(f'SABR: {msg.strip()}')

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
            else:
                self.write_sabr_debug(f'Unhandled part type', part=part, data=part.data)
                continue

    def process_media_header(self, part: UMPPart):
        media_header = protobug.loads(part.data, MediaHeader)
        self.write_sabr_debug(part=part, protobug_obj=media_header, data=part.data)
        if not media_header.format_id:
            raise DownloadError(f'Format ID not found in MediaHeader (media_header={media_header})')

        initialized_format = self.initialized_formats.get(get_format_key(media_header.format_id))
        if not initialized_format:
            self.write_sabr_debug(f'Initialized format not found for {media_header.format_id}', part=part)
            return

        sequence_number = media_header.sequence_number
        if (sequence_number or 0) in initialized_format.sequences:
            self.write_sabr_debug(f'Sequence {sequence_number} already found, skipping', part=part)
            return

        is_init_segment = media_header.is_init_segment
        time_range = media_header.time_range
        start_ms = media_header.start_ms or (time_range and time_range.get_start_ms()) or 0

        # Calculate duration of this segment
        # For videos, either duration_ms or time_range should be present
        # For live streams, calculate segment duration based on live metadata target segment duration
        actual_duration_ms = (
            media_header.duration_ms
            or (time_range and time_range.get_duration_ms()))

        estimated_duration_ms = self.live_metadata and self.live_segment_target_duration_sec * 1000

        duration_ms = actual_duration_ms or estimated_duration_ms or 0

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
                self.write_sabr_debug(
                    part=part, message=f'Created new buffered range for {media_header.format_id} (sabr seeked={self.sabr_seeked}): {initialized_format.buffered_ranges[-1]}')
                return

            end_segment_index = current_buffered_range.end_segment_index or 0
            if end_segment_index != 0 and end_segment_index + 1 != sequence_number:
                raise DownloadError(f'End segment index mismatch: {end_segment_index + 1} != {sequence_number}. Buffered Range: {current_buffered_range}')

            current_buffered_range.end_segment_index = sequence_number

            if not self.live_metadata or actual_duration_ms:
                # We need to increment both duration_ms and time_range.duration
                current_buffered_range.duration_ms += duration_ms
                current_buffered_range.time_range.duration += duration_ms
            else:
                # Attempt to keep in sync with livestream, as the segment duration target is not always perfect.
                # The server seems to care more about the segment index than the duration.
                if current_buffered_range.start_time_ms > start_ms:
                    raise DownloadError(f'Buffered range start time mismatch: {current_buffered_range.start_time_ms} > {start_ms}')

                new_duration = (start_ms - current_buffered_range.start_time_ms) + estimated_duration_ms
                current_buffered_range.duration_ms = current_buffered_range.time_range.duration = new_duration

    def process_media(self, part: UMPPart):
        header_id = part.data[0]

        current_sequence = self.header_ids.get(header_id)
        if not current_sequence:
            self.write_sabr_debug(f'Header ID {header_id} not found', part=part)
            return

        initialized_format = current_sequence.initialized_format

        if not initialized_format:
            self.write_sabr_debug(f'Initialized Format not found for header ID {header_id}', part=part)
            return

        initialized_format.requested_format.write_callback(part.data[1:], SABRStatus(
                fragment_index=current_sequence.sequence_number,
                fragment_count=self.live_metadata and self.live_metadata.latest_sequence_number))
        self._request_had_data = True

    def process_media_end(self, part: UMPPart):
        header_id = part.data[0]
        self.write_sabr_debug(f'Header ID: {header_id}', part=part)
        self.header_ids.pop(header_id, None)

    def process_live_metadata(self, part: UMPPart):
        self.live_metadata = protobug.loads(part.data, LiveMetadata)
        self.write_sabr_debug(part=part, protobug_obj=self.live_metadata, data=part.data)
        if self.live_metadata.latest_sequence_duration_ms:
            self.total_duration_ms = self.live_metadata.latest_sequence_duration_ms

    def process_stream_protection_status(self, part: UMPPart):
        sps = protobug.loads(part.data, StreamProtectionStatus)
        self.write_sabr_debug(f'Status: {StreamProtectionStatus.Status(sps.status).name}', part=part, data=part.data)
        if sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
            raise DownloadError('StreamProtectionStatus: Attestation Required')

    def process_sabr_redirect(self, part: UMPPart):
        sabr_redirect = protobug.loads(part.data, SabrRedirect)
        self.write_sabr_debug(part=part, protobug_obj=sabr_redirect, data=part.data)
        if not sabr_redirect.redirect_url:
            self._logger.warning('SABRRedirect: Invalid redirect URL retrieved. Download may fail.')
            return
        self.server_abr_streaming_url = sabr_redirect.redirect_url
        self._redirected = True

    def process_player_fallback(self):
        # Attempt to fallback to another videoplayback host in the case the current one fails

        qs = parse_qs(self.server_abr_streaming_url)
        parsed_url = urlparse(self.server_abr_streaming_url)
        self._bad_hosts.append(parsed_url.netloc)

        for n in range(0, 5):
            for fh in qs.get('mn', [])[0].split(','):
                fallback = f'rr{n}---{fh}.googlevideo.com'
                if fallback not in self._bad_hosts:
                    fallback_count = int_or_none(qs.get('fallback_count', ['0'])[0], default=0) + 1
                    self.server_abr_streaming_url = parsed_url._replace(netloc=fallback).geturl()
                    self.server_abr_streaming_url = update_url_query(self.server_abr_streaming_url, {'fallback_count': fallback_count})
                    self._logger.warning(f'Failed to connect to {parsed_url.netloc}. Retrying with {fallback}')
                    self._redirected = True
                    return

        self._logger.debug(f'Player fallback failed - no working hosts available. Bad hosts: {self._bad_hosts}')
        raise DownloadError('Player fallback failed')

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
        self.write_sabr_debug(part=part, protobug_obj=fmt_init_metadata, data=part.data)

        initialized_format_key = get_format_key(fmt_init_metadata.format_id)

        if initialized_format_key in self.initialized_formats:
            self.write_sabr_debug('Format already initialized', part)
            return

        matching_requested_format = self._find_matching_requested_format(fmt_init_metadata)

        if not matching_requested_format:
            self.write_sabr_debug(f'Format {initialized_format_key} not in requested formats.. Ignoring', part=part)
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

        self.write_sabr_debug(f'Initialized Format: {initialized_format}', part=part)

    def process_next_request_policy(self, part: UMPPart):
        self.next_request_policy = protobug.loads(part.data, NextRequestPolicy)
        self.write_sabr_debug(part=part, protobug_obj=self.next_request_policy, data=part.data)

    def process_sabr_seek(self, part: UMPPart):
        sabr_seek = protobug.loads(part.data, SabrSeek)
        seek_to = math.ceil((sabr_seek.start / sabr_seek.timescale) * 1000)
        self.write_sabr_debug(part=part, protobug_obj=sabr_seek, data=part.data)
        self.write_sabr_debug(f'Seeking to {seek_to}ms')
        self.client_abr_state.player_time_ms = seek_to
        self.sabr_seeked = True

    def process_sabr_error(self, part: UMPPart):
        sabr_error = protobug.loads(part.data, SabrError)
        self.write_sabr_debug(part=part, protobug_obj=sabr_error, data=part.data)
        raise DownloadError(f'SABR Returned Error: {sabr_error}')

    def _check_expiry(self):
        expires_at = int_or_none(traverse_obj(parse_qs(self.server_abr_streaming_url), ('expire', 0), get_all=False))

        if not expires_at:
            self.write_sabr_debug('No expiry found in server ABR streaming URL. Will not be able to refresh.')
            return

        if expires_at - 300 >= time.time():
            self.write_sabr_debug(f'videoplayback url expires in {int(expires_at - time.time())} seconds')
            return

        self.write_sabr_debug('Refreshing server ABR streaming URL')

        if not self.reload_config_fn:
            raise self._logger.warning(
                'No reload config function found - cannot refresh server ABR streaming URL.'
                ' The url will expire in 5 minutes and the download will fail.')

        # todo: handle errors here and fail gracefully to shutdown the stream
        self.server_abr_streaming_url, self.video_playback_ustreamer_config = self.reload_config_fn()
