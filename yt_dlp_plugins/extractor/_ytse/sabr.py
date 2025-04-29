from __future__ import annotations
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
from yt_dlp.utils._utils import _YDLLogger, RetryManager, bug_reports_message

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
class FormatSelector:
    format_ids: List[FormatId] = dataclasses.field(default_factory=list)
    discard_media: bool = False

    def match(self, format_id: FormatId = None, **kwargs) -> bool:
        return format_id in self.format_ids

@dataclasses.dataclass
class AudioSelector(FormatSelector):

    def match(self, format_id: FormatId = None, mime_type: str = None, **kwargs) -> bool:
        return (
            super().match(format_id, mime_type=mime_type, **kwargs)
            or (not self.format_ids and mime_type and mime_type.lower().startswith('audio'))
        )

@dataclasses.dataclass
class VideoSelector(FormatSelector):

    def match(self, format_id: FormatId = None, mime_type: str = None, **kwargs) -> bool:
        return (
            super().match(format_id, mime_type=mime_type, **kwargs)
            or (not self.format_ids and mime_type and mime_type.lower().startswith('video'))
        )


class SabrStreamConsumedError(DownloadError):
    pass

@dataclasses.dataclass
class SabrPart:
    pass


@dataclasses.dataclass
class MediaSabrPart(SabrPart):
    format_selector: FormatSelector
    format_id: FormatId
    player_time_ms: int = 0
    start_bytes: int = 0
    fragment_index: int = None
    fragment_count: int = None
    is_init_segment: bool = False
    data: bytes = b''


@dataclasses.dataclass
class PoTokenStatusSabrPart(SabrPart):
    class PoTokenStatus(enum.Enum):
        OK = enum.auto()                          # PO Token is provided and valid
        MISSING = enum.auto()                     # PO Token is not provided, and is required. A PO Token should be provided ASAP
        INVALID = enum.auto()                     # PO Token is provided, but is invalid. A new one should be generated ASAP
        PENDING = enum.auto()                     # PO Token is provided, but probably only a cold start token. A full PO Token should be provided ASAP
        NOT_REQUIRED = enum.auto()                # PO Token is not provided, and is not required
        PENDING_MISSING = enum.auto()             # PO Token is not provided, but is pending. A full PO Token should be (probably) provided ASAP

    status: PoTokenStatus


@dataclasses.dataclass
class Segment:
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
    format_selector: FormatSelector | None = None
    duration_ms: int = 0
    end_time_ms: int = 0
    mime_type: str = None
    current_segment: Segment | None = None
    init_segment: Segment | None = None
    buffered_ranges: List[BufferedRange] = dataclasses.field(default_factory=list)
    total_sequences: int = None


def get_format_key(format_id: FormatId):
    return f'{format_id.itag}-{format_id.lmt}-{format_id.xtags}'


class SABRStream:
    def __init__(
        self,
        urlopen: typing.Callable[[Request], Response],
        logger: _YDLLogger,
        server_abr_streaming_url: str,
        video_playback_ustreamer_config: str,
        client_info: ClientInfo,
        audio_selection: AudioSelector = None,
        video_selection: VideoSelector = None,
        live_segment_target_duration_sec: int = None,
        reload_config_fn: typing.Callable[[], tuple[str, str]] = None,
        start_time_ms: int = 0,
        debug=False,
        po_token: str = None,
        http_retries: int = 3,
        live_end_wait_sec: int = 10,
    ):

        self._logger = logger
        self._debug = debug
        self._urlopen = urlopen

        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token = po_token
        self.reload_config_fn = reload_config_fn
        self.client_info = client_info
        self.live_segment_target_duration_sec = live_segment_target_duration_sec or 5
        self.start_time_ms = start_time_ms
        self.http_retries = http_retries
        self.live_end_wait_sec = live_end_wait_sec

        if self.live_segment_target_duration_sec:
            self.write_sabr_debug(f'using live_segment_target_duration_sec: {self.live_segment_target_duration_sec}')

        self._audio_format_selector = audio_selection
        self._video_format_selector = video_selection

        if not self._audio_format_selector and not self._video_format_selector:
            raise DownloadError('No audio or video requested')

        # State management
        self._requests_no_data = 0
        self._timestamp_no_data = None
        self._request_number = 0

        self._sps_retry_count = 0
        self._is_retry = False
        self._default_max_sps_retries = 5

        self._redirected = False
        self._request_had_data = False
        self._sabr_seeked = False
        self._header_ids: dict[int, Segment] = {}
        self._bad_hosts = []

        self._total_duration_ms = None

        self._selected_audio_format_ids = []
        self._selected_video_format_ids = []
        self._next_request_policy: NextRequestPolicy | None = None
        self._live_metadata: LiveMetadata | None = None
        self._client_abr_state: ClientAbrState
        self._initialized_formats: dict[str, InitializedFormat] = {}

        self._consumed = False

        self._initialize_cabr_state()

    def __iter__(self):
        return self.iter_parts()

    def _initialize_cabr_state(self):
        # note: video only is not supported
        enabled_track_types_bitfield = 0  # Both
        if not self._video_format_selector:
            enabled_track_types_bitfield = 1  # Audio only
            # Guard against audio-only returning video formats
            self._video_format_selector = VideoSelector(discard_media=True)

        if not self._audio_format_selector:
            self._audio_format_selector = AudioSelector(discard_media=True)

        self._selected_audio_format_ids = self._audio_format_selector.format_ids
        self._selected_video_format_ids = self._video_format_selector.format_ids

        self.write_sabr_debug(f'starting at: {self.start_time_ms}')
        self._client_abr_state = ClientAbrState(
            player_time_ms=self.start_time_ms,
            enabled_track_types_bitfield=enabled_track_types_bitfield,
        )

    def iter_parts(self, max_requests=-1):
        if self._consumed:
            raise SabrStreamConsumedError('SABR stream has already been consumed')

        while not self._consumed:
            self.process_expiry()
            vpabr = VideoPlaybackAbrRequest(
                client_abr_state=self._client_abr_state,
                selected_video_format_ids=self._selected_video_format_ids,
                selected_audio_format_ids=self._selected_audio_format_ids,
                selected_format_ids=[
                    initialized_format.format_id for initialized_format in self._initialized_formats.values()
                ],
                video_playback_ustreamer_config=base64.urlsafe_b64decode(self.video_playback_ustreamer_config),
                streamer_context=StreamerContext(
                     po_token=self.po_token and base64.urlsafe_b64decode(self.po_token),
                     playback_cookie=self._next_request_policy and protobug.dumps(self._next_request_policy.playback_cookie),
                     client_info=self.client_info
                 ),
                buffered_ranges=[
                    buffered_range for initialized_format in self._initialized_formats.values()
                    for buffered_range in initialized_format.buffered_ranges
                ],
            )
            payload = protobug.dumps(vpabr)
            self.write_sabr_debug(f'video_playback_ustreamer_config: {self.video_playback_ustreamer_config}')
            self.write_sabr_debug(f'Sending videoplayback SABR request: {vpabr}')

            # Attempt to retry the request if there is an intermittent network issue.
            # Otherwise, it may be a server issue, so try to fall back to another host.
            try:
                for retry in RetryManager(self.http_retries, self._report_retry):
                    response = None
                    try:
                        response = self._urlopen(
                            Request(
                                url=self.server_abr_streaming_url,
                                method='POST',
                                data=payload,
                                query={'rn': self._request_number},
                                headers={'content-type': 'application/x-protobuf'}
                            )
                        )
                        self._request_number += 1
                        # Handle read errors too
                        yield from filter(None, self.parse_ump_response(response))
                    except TransportError as e:
                        self._logger.warning(f'Transport Error: {e}')
                        retry.error = e
                        continue
                    finally:
                        # For when response is not entirely read, ensure it is closed.
                        if response and not response.closed:
                            response.close()

            except HTTPError as e:
                self._logger.debug(f'HTTP Error: {e.status} - {e.reason}')
                # on 5xx errors, if a retry does not work, try falling back to another host?
                if 500 <= e.status < 600:
                    self.process_gvs_fallback()
                else:
                    raise DownloadError(f'HTTP Error: {e.status} - {e.reason}')

            except TransportError as e:
                self._logger.warning(f'Transport Error: {e}')
                self.process_gvs_fallback()

            self._prepare_next_request()

        self._consumed = True

    def _prepare_next_request(self):
        if len(self._header_ids):
            self._logger.warning(f'Extraneous header IDs left: {list(self._header_ids.values())}')
            self._header_ids.clear()

        wait_seconds = 0

        # Do not update client abr state if we are retrying
        # For the case we fail midway through a response after reading some media data, but didn't get all of it.
        if not self._is_retry:
            # Don't count retries e.g. SPS.
            # As any retry logic should not be sending us in infinite requests
            if not self._request_had_data:
                self._requests_no_data += 1
                if not self._timestamp_no_data:
                    self._timestamp_no_data = time.time()
            else:
                self._requests_no_data = 0
                self._timestamp_no_data = None


            # TODO: should consider storing only one buffered range?
            # TODO: For concurrency, we'll likely sync SabrStream buffered ranges to avoid re-downloading segments. This may require more than one buffered range?
            # In this case, we'll need to find the buffered range to use by player_time_ms?
            current_buffered_ranges = [
                initialized_format.buffered_ranges[-1]
                for initialized_format in self._initialized_formats.values() if initialized_format.buffered_ranges
            ]

            # choose format that is the most behind
            lowest_buffered_range = min(current_buffered_ranges, key=lambda x: x.start_time_ms + x.duration_ms) if current_buffered_ranges else None
            min_buffered_duration_ms = lowest_buffered_range.start_time_ms + lowest_buffered_range.duration_ms if lowest_buffered_range else 0
            next_request_backoff_ms = (self._next_request_policy and self._next_request_policy.backoff_time_ms) or 0

            # TODO: we should also consider incrementing player_time_ms if we already had all segments (i.e. check which segments we skipped and why)
            #  Generally, next_request_policy backoff_time_ms will set this but we should also default it to not rely on it

            request_player_time = self._client_abr_state.player_time_ms
            self._client_abr_state.player_time_ms = max(
                min_buffered_duration_ms,
                # next request policy backoff_time_ms is the minimum to increment player_time_ms by
                self._client_abr_state.player_time_ms + next_request_backoff_ms,
            )

            # Check if the latest segment is the last one of each format (if data is available)
            # TODO: fallback livestream handling when we don't have live_metadata
            # TODO: check current sequence number instead of buffered ranges
            if (
                not self._live_metadata
                and self._initialized_formats
                and len(current_buffered_ranges) == len(self._initialized_formats)
                and all(
                    (
                        initialized_format.buffered_ranges
                        and initialized_format.buffered_ranges[-1].end_segment_index is not None
                        and initialized_format.total_sequences is not None
                        and initialized_format.buffered_ranges[-1].end_segment_index == initialized_format.total_sequences
                    )
                    for initialized_format in self._initialized_formats.values()
                )
            ):
                self.write_sabr_debug(f'Reached last segment for all formats, assuming end of media')
                self._consumed = True

            # Check if we have exceeded the total duration of the media (if not live),
            #  or wait for the next segment (if live)
            # TODO: should consider live stream timestamp in LIVE_METADATA perhaps?
            elif self._total_duration_ms and (self._client_abr_state.player_time_ms >= self._total_duration_ms):
                if self._live_metadata:
                    self._client_abr_state.player_time_ms = self._total_duration_ms
                    # TODO: we need this for live streams in the case there is no live_metadata
                    if (
                        self._requests_no_data > 3
                        and self._timestamp_no_data
                        and self._timestamp_no_data < time.time() + self.live_end_wait_sec
                    ):
                        self._logger.debug(f'No fragments received for at least {self.live_end_wait_sec} seconds, assuming end of live stream')
                        self._consumed = True
                    else:
                        wait_seconds = (next_request_backoff_ms // 1000) + self.live_segment_target_duration_sec
                else:
                    self.write_sabr_debug(f'End of media (player time ms {self._client_abr_state.player_time_ms} >= total duration ms {self._total_duration_ms})')
                    self._consumed = True

            # Guard against receiving no data before end of video/stream
            if (
                (not self._total_duration_ms or (self._client_abr_state.player_time_ms < self._total_duration_ms))
                and request_player_time == self._client_abr_state.player_time_ms
                and not self._consumed
                and self._requests_no_data > 3
            ):
                raise DownloadError('No data found in three consecutive requests')

        self._next_request_policy = None
        self._sabr_seeked = False
        self._redirected = False
        self._is_retry = False
        self._request_had_data = False

        # TODO: clear buffered ranges that are not behind or in front of current player time ms
        if not self._consumed:
            self.write_sabr_debug(f'Next request player time ms: {self._client_abr_state.player_time_ms}, total duration ms: {self._total_duration_ms}')

        if wait_seconds:
            self.write_sabr_debug(f'sleeping {wait_seconds} seconds for next fragment')
            time.sleep(wait_seconds)

    def _report_retry(self, err, count, retries, fatal=True):
        RetryManager.report_retry(
            err, count, retries, info=self._logger.info,
            warn=lambda msg: self._logger.warning(f'[download] Got error: {msg}'),
            error=None if fatal else lambda msg: self._logger.warning(f'[download] Got error: {msg}'),
            sleep_func=0  # todo: use sleep func configuration
        )

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
        # xxx: this should handle the same response being provided multiple times with without issue. need to test.
        ump = UMPParser(response)
        for part in ump.iter_parts():
            if part.part_type == UMPPartType.MEDIA_HEADER:
                self.process_media_header(part)
            elif part.part_type == UMPPartType.MEDIA:
                yield self.process_media(part)
            elif part.part_type == UMPPartType.MEDIA_END:
                self.process_media_end(part)
            elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                yield self.process_stream_protection_status(part)
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

        initialized_format = self._initialized_formats.get(get_format_key(media_header.format_id))
        if not initialized_format:
            self.write_sabr_debug(f'Initialized format not found for {media_header.format_id}', part=part)
            return

        sequence_number, is_init_segment = media_header.sequence_number, media_header.is_init_segment

        if sequence_number is None and not media_header.is_init_segment:
            raise DownloadError(f'Sequence number not found in MediaHeader (media_header={media_header})', part=part)

        # Note: previous segment should never be an init segment
        previous_segment = initialized_format.current_segment
        if previous_segment:
            if sequence_number <= previous_segment.sequence_number:
                self.write_sabr_debug(f'Segment {sequence_number} before or same as previous segment, skipping as probably already seen', part=part)
                return

            if sequence_number != previous_segment.sequence_number + 1:
                # Bail out as the segment is not in order when it should be
                # TODO: logging should include plenty of info, including previous segment, whether we sabr seeked, etc.
                raise DownloadError(f'Segment sequence number mismatch: {previous_segment.sequence_number + 1} != {sequence_number}')

        time_range = media_header.time_range
        start_ms = media_header.start_ms or (time_range and time_range.get_start_ms()) or 0

        # Calculate duration of this segment
        # For videos, either duration_ms or time_range should be present
        # For live streams, calculate segment duration based on live metadata target segment duration
        actual_duration_ms = (
            media_header.duration_ms
            or (time_range and time_range.get_duration_ms()))

        estimated_duration_ms = self._live_metadata and self.live_segment_target_duration_sec * 1000
        duration_ms = actual_duration_ms or estimated_duration_ms or 0

        segment = Segment(
            format_id=media_header.format_id,
            is_init_segment=is_init_segment,
            duration_ms=duration_ms,
            start_data_range=media_header.start_data_range,
            sequence_number=sequence_number,
            content_length=media_header.content_length,
            start_ms=start_ms,
            initialized_format=initialized_format
        )

        self._header_ids[media_header.header_id] = segment

        if is_init_segment:
            initialized_format.init_segment = segment
            # Do not create a buffered range for init segments
            return

        initialized_format.current_segment = segment

        # Try find matching buffered range this segment belongs to
        buffered_range = next(
            (br for br in initialized_format.buffered_ranges if br.end_segment_index == sequence_number - 1),
            None
        )

        if not buffered_range:
            # Create a new buffered range
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
                part=part, message=f'Created new buffered range for {media_header.format_id} {initialized_format.buffered_ranges[-1]}')
            return

        buffered_range.end_segment_index = sequence_number
        if not self._live_metadata or actual_duration_ms:
            # We need to increment both duration_ms and time_range.duration
            buffered_range.duration_ms += duration_ms
            buffered_range.time_range.duration += duration_ms
        else:
            # Attempt to keep in sync with livestream, as the segment duration target is not always perfect.
            # The server seems to care more about the segment index than the duration.
            if buffered_range.start_time_ms > start_ms:
                raise DownloadError(f'Buffered range start time mismatch: {buffered_range.start_time_ms} > {start_ms}')

            new_duration = (start_ms - buffered_range.start_time_ms) + estimated_duration_ms
            buffered_range.duration_ms = buffered_range.time_range.duration = new_duration

    def process_media(self, part: UMPPart):
        header_id = part.data[0]
        segment = self._header_ids.get(header_id)
        if not segment:
            self.write_sabr_debug(f'Header ID {header_id} not found', part=part)
            return

        initialized_format = segment.initialized_format

        if not initialized_format:
            self.write_sabr_debug(f'Initialized Format not found for header ID {header_id}', part=part)
            return

        # Will count discard (ignored) media as a request with data... as something is at least coming through
        self._request_had_data = True

        if initialized_format.format_selector.discard_media:
            return

        return MediaSabrPart(
            format_selector=initialized_format.format_selector,
            format_id=segment.format_id,
            player_time_ms=self._client_abr_state.player_time_ms,
            fragment_index=segment.sequence_number,
            fragment_count=self._live_metadata and self._live_metadata.head_sequence_number,
            data=part.data[1:],
            is_init_segment=segment.is_init_segment
        )

    def process_media_end(self, part: UMPPart):
        # TODO: should probably publish a media end event so it knows when to stop writing fragment
        header_id = part.data[0]
        self.write_sabr_debug(f'Header ID: {header_id}', part=part)
        self._header_ids.pop(header_id, None)

    def process_live_metadata(self, part: UMPPart):
        self._live_metadata = protobug.loads(part.data, LiveMetadata)
        self.write_sabr_debug(part=part, protobug_obj=self._live_metadata, data=part.data)
        if self._live_metadata.head_sequence_time_ms:
            self._total_duration_ms = self._live_metadata.head_sequence_time_ms

    def process_stream_protection_status(self, part: UMPPart):
        sps = protobug.loads(part.data, StreamProtectionStatus)
        self.write_sabr_debug(f'Status: {StreamProtectionStatus.Status(sps.status).name}. SPS Retry: {self._sps_retry_count}', protobug_obj=sps, part=part, data=part.data)
        if sps.status == StreamProtectionStatus.Status.OK:
            self._sps_retry_count = 0
            if self.po_token:
                return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.OK)
            return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.NOT_REQUIRED)
        elif sps.status == StreamProtectionStatus.Status.ATTESTATION_PENDING:
            if sps.max_retries is not None:
                # Should not happen
                self._logger.warning(f'StreamProtectionStatus: Attestation Pending has a retry count of {sps.max_retries}{bug_reports_message()}')
            if self.po_token:
                return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.PENDING)
            return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.PENDING_MISSING)
        elif sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
            if self._sps_retry_count >= (sps.max_retries or self._default_max_sps_retries):
                raise DownloadError(f'StreamProtectionStatus: Attestation Required ({"Invalid" if self.po_token else "Missing"} PO Token)')

            # xxx: temporal network error retries, host changes due to errors will count towards the SPS retry
            self._sps_retry_count += 1
            self._is_retry = True

            if self.po_token:
                return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.INVALID)
            return PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.MISSING)
        return None

    def process_sabr_redirect(self, part: UMPPart):
        sabr_redirect = protobug.loads(part.data, SabrRedirect)
        self.write_sabr_debug(part=part, protobug_obj=sabr_redirect, data=part.data)
        if not sabr_redirect.redirect_url:
            self._logger.warning('SABRRedirect: Invalid redirect URL retrieved. Download may fail.')
            return
        self.server_abr_streaming_url = sabr_redirect.redirect_url
        self._redirected = True

    def process_gvs_fallback(self):
        # Attempt to fall back to another GVS host in the case the current one fails
        qs = parse_qs(self.server_abr_streaming_url)
        parsed_url = urlparse(self.server_abr_streaming_url)
        self._bad_hosts.append(parsed_url.netloc)

        for n in range(1, 5):
            for fh in qs.get('mn', [])[0].split(','):
                fallback = f'rr{n}---{fh}.googlevideo.com'
                if fallback not in self._bad_hosts:
                    fallback_count = int_or_none(qs.get('fallback_count', ['0'])[0], default=0) + 1
                    self.server_abr_streaming_url = update_url_query(
                        parsed_url._replace(netloc=fallback).geturl(), {'fallback_count': fallback_count})
                    self._logger.warning(f'Failed to connect to GVS host {parsed_url.netloc}. Retrying with GVS host {fallback}')
                    self._redirected = True
                    self._is_retry = True
                    return

        self._logger.debug(f'GVS fallback failed - no working hosts available. Bad hosts: {self._bad_hosts}')
        raise DownloadError('Unable to find a working Google Video Server. Is your connection okay?')

    def _match_format_selector(self, format_init_metadata: FormatInitializationMetadata):
        for format_selector in (self._video_format_selector, self._audio_format_selector):
            if not format_selector:
                continue
            if format_selector.match(format_id=format_init_metadata.format_id, mime_type=format_init_metadata.mime_type):
                return format_selector
        return None

    def process_format_initialization_metadata(self, part: UMPPart):
        fmt_init_metadata = protobug.loads(part.data, FormatInitializationMetadata)
        self.write_sabr_debug(part=part, protobug_obj=fmt_init_metadata, data=part.data)

        initialized_format_key = get_format_key(fmt_init_metadata.format_id)
        if initialized_format_key in self._initialized_formats:
            self.write_sabr_debug('Format already initialized', part)
            return

        format_selector = self._match_format_selector(fmt_init_metadata)

        if not format_selector:
            self._logger.warning(f'Format {initialized_format_key} not in requested formats.. Ignoring')
            return

        duration_ms = (
                fmt_init_metadata.duration
                and math.ceil((fmt_init_metadata.duration / fmt_init_metadata.duration_timescale) * 1000)
        )

        initialized_format = InitializedFormat(
            format_id=fmt_init_metadata.format_id,
            duration_ms=duration_ms,
            end_time_ms=fmt_init_metadata.end_time_ms,
            mime_type=fmt_init_metadata.mime_type,
            video_id=fmt_init_metadata.video_id,
            format_selector=format_selector,
            total_sequences=fmt_init_metadata.total_segments,
        )
        self._total_duration_ms = max(self._total_duration_ms or 0, fmt_init_metadata.end_time_ms or 0, duration_ms or 0)
        self._initialized_formats[get_format_key(fmt_init_metadata.format_id)] = initialized_format

        self.write_sabr_debug(f'Initialized Format: {initialized_format}', part=part)

    def process_next_request_policy(self, part: UMPPart):
        self._next_request_policy = protobug.loads(part.data, NextRequestPolicy)
        self.write_sabr_debug(part=part, protobug_obj=self._next_request_policy, data=part.data)

    def process_sabr_seek(self, part: UMPPart):
        # TODO: disallow sabr seek for normal videos?
        sabr_seek = protobug.loads(part.data, SabrSeek)
        seek_to = math.ceil((sabr_seek.seek_time / sabr_seek.timescale) * 1000)
        self.write_sabr_debug(part=part, protobug_obj=sabr_seek, data=part.data)
        self.write_sabr_debug(f'Seeking to {seek_to}ms')
        self._client_abr_state.player_time_ms = seek_to
        self._sabr_seeked = True

        # Clear latest segment as will no longer be in order
        for initialized_format in self._initialized_formats.values():
            initialized_format.current_segment = None

    def process_sabr_error(self, part: UMPPart):
        sabr_error = protobug.loads(part.data, SabrError)
        self.write_sabr_debug(part=part, protobug_obj=sabr_error, data=part.data)
        raise DownloadError(f'SABR Returned Error: {sabr_error}')

    def process_expiry(self):
        expires_at = int_or_none(traverse_obj(parse_qs(self.server_abr_streaming_url), ('expire', 0), get_all=False))

        if not expires_at:
            self.write_sabr_debug('No expiry found in SABR streaming URL. Will not be able to refresh.')
            return

        if expires_at - 300 >= time.time():
            self.write_sabr_debug(f'SABR streaming url expires in {int(expires_at - time.time())} seconds')
            return

        self.write_sabr_debug('Refreshing SABR streaming URL')

        if not self.reload_config_fn:
            raise self._logger.warning(
                'No reload config function found - cannot refresh SABR streaming URL.'
                ' The url will expire in 5 minutes and the download will fail.')

        try:
            self.server_abr_streaming_url, self.video_playback_ustreamer_config = self.reload_config_fn()
        except (TransportError, HTTPError) as e:
            raise DownloadError(f'Failed to refresh SABR streaming URL: {e}') from e
