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
from yt_dlp import int_or_none, traverse_obj
from yt_dlp.networking import Request, Response
from yt_dlp.networking.exceptions import HTTPError, TransportError
from yt_dlp.utils import parse_qs, update_url_query
from yt_dlp.utils._utils import _YDLLogger, RetryManager, bug_reports_message, YoutubeDLError

from .protos import unknown_fields
from .protos.videostreaming.buffered_range import BufferedRange
from .protos.videostreaming.client_abr_state import ClientAbrState
from .protos.videostreaming.format_id import FormatId
from .protos.videostreaming.media_header import MediaHeader
from .protos.videostreaming.streamer_context import StreamerContext
from .protos.videostreaming.video_playback_abr_request import VideoPlaybackAbrRequest
from .protos.videostreaming.live_metadata import LiveMetadata
from .protos.videostreaming.time_range import TimeRange
from .protos.videostreaming.stream_protection_status import StreamProtectionStatus
from .protos.videostreaming.sabr_redirect import SabrRedirect
from .protos.videostreaming.format_initialization_metadata import FormatInitializationMetadata
from .protos.videostreaming.sabr_seek import SabrSeek
from .protos.videostreaming.sabr_error import SabrError

from .protos.innertube.client_info import ClientInfo
from .protos.innertube.next_request_policy import NextRequestPolicy

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


class SabrStreamConsumedError(YoutubeDLError):
    pass


class SabrStreamError(YoutubeDLError):
    pass


@dataclasses.dataclass
class SabrPart:
    pass


@dataclasses.dataclass
class MediaSegmentSabrPart(SabrPart):
    format_selector: FormatSelector
    format_id: FormatId
    player_time_ms: int = 0
    start_bytes: int = None
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
class RefreshPlayerResponseSabrPart(SabrPart):

    class Reason(enum.Enum):
        UNKNOWN = enum.auto()
        SABR_URL_EXPIRY = enum.auto()

    reason: Reason

@dataclasses.dataclass
class MediaSeekSabrPart(SabrPart):
    # Lets the caller know the media sequence for a format may change
    class Reason(enum.Enum):
        UNKNOWN = enum.auto()
        SERVER_SEEK = enum.auto()  # SABR_SEEK from server
        BUFFER_SEEK = enum.auto()  # Seeking as next fragment is already buffered

    reason: Reason
    format_id: FormatId
    format_selector: FormatSelector


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
    # Whether duration_ms is an estimate
    duration_estimated: bool = False
    # Whether we should discard the segment data
    discard: bool = False
    data: bytes = b''


@dataclasses.dataclass
class InitializedFormat:
    format_id: FormatId
    video_id: str
    format_selector: FormatSelector | None = None
    duration_ms: int = 0
    end_time_ms: int = 0
    mime_type: str = None
    # Current segment in the sequence. Set to None to break the sequence and allow a seek.
    current_segment: Segment | None = None
    init_segment: Segment | None = None
    buffered_ranges: List[BufferedRange] = dataclasses.field(default_factory=list)
    total_sequences: int = None
    # Whether we should discard any data received for this format
    discard: bool = False

JS_MAX_SAFE_INTEGER = (2**53) - 1

class SabrStream:

    """

    A YouTube SABR (Server Abr Bit Rate) client implementation that is not bound to a real player time.
    It essentially converts the server side controlled playback to client side controlled playback.

    (todo: better description lol)

    It presents an iterator that yields the next available segments and other metadata.

    Buffer tracking:
    SabrStream keeps track of what segments it has seen and tells the server to not send them again.
    This includes after a seek (e.g. SABR_SEEK).

    TODO:
    - Retry logic is completely broken and causes the video to skip all over the place
    - Handling for live_metadata not being present
    - Improved logging for debugging (unexpected errors / warnings should contain enough context to debug them)
    - Unit testing various scenarios, particularly the edge cases
    - Increment player_time_ms if we received segments in the request (inc skipped as already seen)
    - Decouple logger from YDL
    """

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
            raise SabrStreamError('No audio or video requested')

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

    def close(self):
        self._consumed = True


    def __iter__(self):
        return self.iter_parts()

    def _initialize_cabr_state(self):
        # note: video only is not supported
        enabled_track_types_bitfield = 0  # Audio+Video
        if not self._video_format_selector:
            enabled_track_types_bitfield = 1  # Audio only
            # Guard against audio-only returning video formats
            self._video_format_selector = VideoSelector(discard_media=True)

        # SABR does not support video-only, so we need to discard the audio track received.
        # We need a selector as the server sometimes does not like it
        # if we haven't initialized an audio format (e.g. livestreams).
        if not self._audio_format_selector:
            self._audio_format_selector = AudioSelector(discard_media=True)

        self._selected_audio_format_ids = self._audio_format_selector.format_ids
        self._selected_video_format_ids = self._video_format_selector.format_ids

        self.write_sabr_debug(f'starting at: {self.start_time_ms}')
        self._client_abr_state = ClientAbrState(
            player_time_ms=self.start_time_ms,
            enabled_track_types_bitfield=enabled_track_types_bitfield,
        )

    def iter_parts(self):
        if self._consumed:
            raise SabrStreamConsumedError('SABR stream has already been consumed')

        while not self._consumed:
            yield from self.process_expiry()
            vpabr = VideoPlaybackAbrRequest(
                client_abr_state=self._client_abr_state,
                selected_video_format_ids=self._selected_video_format_ids,
                selected_audio_format_ids=self._selected_audio_format_ids,
                initialized_format_ids=[
                    initialized_format.format_id for initialized_format in self._initialized_formats.values()
                ],
                video_playback_ustreamer_config=base64.urlsafe_b64decode(self.video_playback_ustreamer_config),
                streamer_context=StreamerContext(
                     po_token=self.po_token and base64.urlsafe_b64decode(self.po_token),
                     playback_cookie=self._next_request_policy and self._next_request_policy.playback_cookie,
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

            response = self._request_sabr(payload)

            # TODO: handle errors on read. However, need to be careful as the state has been partially changed
            # But may not have retrieved all parts
            # e.g. When we get a MediaHeader, we increase the buffered range then. Perhaps we should do it on the MediaEnd?
            yield from self.parse_ump_response(response)
            yield from self._prepare_next_request()

        self._consumed = True

    def _request_sabr(self, payload):
        # Attempt to retry the request if there is an intermittent network issue.
        # Otherwise, it may be a server issue, so try to fall back to another host.
        try:
            for retry in RetryManager(self.http_retries, self._report_retry):
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
                    return response
                except TransportError as e:
                    self._logger.warning(f'Transport Error: {e}')
                    retry.error = e
                    continue
            return None
        except HTTPError as e:
            self._logger.debug(f'HTTP Error: {e.status} - {e.reason}')
            # on 5xx errors, if a retry does not work, try falling back to another host?
            # todo: retry the request here?
            if 500 <= e.status < 600:
                self.process_gvs_fallback()
                return None
            else:
                raise SabrStreamError(f'HTTP Error: {e.status} - {e.reason}')

        except TransportError as e:
            self._logger.warning(f'Transport Error: {e}')
            self.process_gvs_fallback()
            return None

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


            for izf in self._initialized_formats.values():
                if not izf.current_segment:
                    continue

                # Guard: Check that the segment is not in multiple buffered ranges
                # This should not happen, but if it does, we should bail
                count = sum(
                    1 for br in izf.buffered_ranges
                    if br.start_segment_index <= izf.current_segment.sequence_number <= br.end_segment_index
                )

                if count > 1:
                    raise SabrStreamError(f'Segment {izf.current_segment.sequence_number} in multiple buffered ranges: {count}')

                # Check if there is two buffered ranges where the end lines up with the start of the other.
                # This could happen in the case of where we seeked backwards (for whatever reason, e.g. livestream)
                # In this case, we should consider a seek as acceptable to the end of the other.
                # Note: It is assumed a segment is only present in one buffered range - it should not be allowed in multiple (by process media header)
                prev_buffered_range = next(
                    (br for br in izf.buffered_ranges if br.end_segment_index == izf.current_segment.sequence_number),
                    None
                )
                if prev_buffered_range and len(get_br_chain(prev_buffered_range, izf.buffered_ranges)) >= 2:
                    self.write_sabr_debug(f'Found two buffered ranges that line up, allowing a seek for format {izf.format_id}')
                    izf.current_segment = None
                    yield MediaSeekSabrPart(
                        reason=MediaSeekSabrPart.Reason.BUFFER_SEEK,
                        format_id=izf.format_id,
                        format_selector=izf.format_selector,
                    )

            # For each initialized format:
            #   1. find the buffered format that matches player_time_ms.
            #   2. find the last buffered range in sequence (in case multiple are joined together)
            latest_buffered_ranges = []
            for izf in self._initialized_formats.values():
                for br in izf.buffered_ranges:
                    if br.start_time_ms <= self._client_abr_state.player_time_ms <= br.start_time_ms + br.duration_ms:
                        chain = get_br_chain(br, izf.buffered_ranges)
                        latest_buffered_ranges.append(chain[-1])
                        break # There should only be one chain for player_time_ms


            # Then set the player_time_ms to the lowest buffered range end of the initialized formats
            lowest_izf_buffered_range = min(latest_buffered_ranges, key=lambda br: br.start_time_ms + br.duration_ms)
            min_buffered_duration_ms = lowest_izf_buffered_range.start_time_ms + lowest_izf_buffered_range.duration_ms

            if len(latest_buffered_ranges) != len(self._initialized_formats):
                # Missing a buffered range for a format - likely a format was seeked?
                # In this case, consider player_time_ms to be our correct next time
                # May? happen in the case of:
                # 1. SABR_SEEK to Time outside both formats buffered ranges
                # 2. ONE of the formats returns data after the SABR_SEEK in that request
                min_buffered_duration_ms = min(min_buffered_duration_ms, self._client_abr_state.player_time_ms)

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
            if (
                not self._live_metadata
                and self._initialized_formats
                and len(latest_buffered_ranges) == len(self._initialized_formats)
                and all(
                    (
                        initialized_format.discard or
                        (
                            initialized_format.buffered_ranges
                            and initialized_format.buffered_ranges[-1].end_segment_index is not None
                            and initialized_format.total_sequences is not None
                            and initialized_format.buffered_ranges[-1].end_segment_index >= initialized_format.total_sequences
                        )
                    )
                    for initialized_format in self._initialized_formats.values()
                )
            ):
                self.write_sabr_debug(f'Reached last segment for all formats, assuming end of media')
                self._consumed = True

            # Check if we have exceeded the total duration of the media (if not live),
            #  or wait for the next segment (if live)
            elif self._total_duration_ms and (self._client_abr_state.player_time_ms >= self._total_duration_ms):
                if self._live_metadata:
                    self._client_abr_state.player_time_ms = self._total_duration_ms
                    # TODO: we need this for live streams in the case there is no live_metadata
                    if (
                        self._requests_no_data > 3
                        and self._timestamp_no_data
                        and not self._redirected
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
            # TODO: add a fallback here for livestreams, if we can't get the total_duration_ms or live_metadata doesn't exist
            if (
                (not self._total_duration_ms or (self._client_abr_state.player_time_ms < self._total_duration_ms))
                and request_player_time == self._client_abr_state.player_time_ms
                and not self._consumed
                and not self._redirected
                and self._requests_no_data > 3
            ):
                raise SabrStreamError('No data found in three consecutive requests')

        self._next_request_policy = None
        self._redirected = False
        self._is_retry = False
        self._request_had_data = False

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
                self.process_media(part)
            elif part.part_type == UMPPartType.MEDIA_END:
                yield from self.process_media_end(part)
            elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                yield from self.process_stream_protection_status(part)
            elif part.part_type == UMPPartType.SABR_REDIRECT:
                self.process_sabr_redirect(part)
            elif part.part_type == UMPPartType.FORMAT_INITIALIZATION_METADATA:
                self.process_format_initialization_metadata(part)
            elif part.part_type == UMPPartType.NEXT_REQUEST_POLICY:
                self.process_next_request_policy(part)
            elif part.part_type == UMPPartType.LIVE_METADATA:
                self.process_live_metadata(part)
            elif part.part_type == UMPPartType.SABR_SEEK:
                yield from self.process_sabr_seek(part)
            elif part.part_type == UMPPartType.SABR_ERROR:
                self.process_sabr_error(part)
            else:
                self.write_sabr_debug(f'Unhandled part type', part=part, data=part.data)
                continue

    def process_media_header(self, part: UMPPart):
        media_header = protobug.loads(part.data, MediaHeader)
        self.write_sabr_debug(part=part, protobug_obj=media_header, data=part.data)
        if not media_header.format_id:
            raise SabrStreamError(f'Format ID not found in MediaHeader (media_header={media_header})')

        # Guard. This should not happen, except if we don't clear partial segments
        if media_header.header_id in self._header_ids:
            raise SabrStreamError(f'Header ID {media_header.header_id} already exists')

        if media_header.compression:
            # Unknown when this is used, but it is not supported
            raise SabrStreamError(f'Compression not supported in MediaHeader (media_header={media_header})')

        initialized_format = self._initialized_formats.get(str(media_header.format_id))
        if not initialized_format:
            self.write_sabr_debug(f'Initialized format not found for {media_header.format_id}', part=part)
            return

        sequence_number, is_init_segment = media_header.sequence_number, media_header.is_init_segment
        if sequence_number is None and not media_header.is_init_segment:
            raise SabrStreamError(f'Sequence number not found in MediaHeader (media_header={media_header})')

        discard = initialized_format.discard
        # Guard: Check if sequence number is within any existing buffered range
        # The server should not send us any segments that are already buffered
        # However, if retrying a request, we may get the same segment again
        if not is_init_segment and any(
            (
                br.start_segment_index <= sequence_number <= br.end_segment_index
                for br in initialized_format.buffered_ranges
            )
        ):
            self.write_sabr_debug(f'Segment {sequence_number} already buffered, marking to discard', part=part)
            discard = True

        # Note: previous segment should never be an init segment
        # Note: we don't care if formats/segments to discard are out of order
        #  (this can be expected if discarding audio - video format may be more ahead slightly)
        previous_segment = initialized_format.current_segment
        if previous_segment and not is_init_segment and not discard:
            if sequence_number <= previous_segment.sequence_number:
                self.write_sabr_debug(f'Segment {sequence_number} before or same as previous segment, will discard as probably already seen', part=part)
                discard = True

            elif sequence_number != previous_segment.sequence_number + 1:
                # Bail out as the segment is not in order when it is expected to be
                raise SabrStreamError(f'Segment sequence number mismatch: {previous_segment.sequence_number + 1} != {sequence_number}')

        if initialized_format.init_segment and is_init_segment:
            self.write_sabr_debug(f'Init segment {sequence_number} already seen, marking as discard', part=part)
            discard = True

        time_range = media_header.time_range
        start_ms = media_header.start_ms or (time_range and time_range.get_start_ms()) or 0

        # Calculate duration of this segment
        # For videos, either duration_ms or time_range should be present
        # For live streams, calculate segment duration based on live metadata target segment duration
        actual_duration_ms = (
            media_header.duration_ms
            or (time_range and time_range.get_duration_ms()))

        estimated_duration_ms = None
        if self._live_metadata:
            estimated_duration_ms = self.live_segment_target_duration_sec * 1000

        # TODO: should this really default to 0?
        #  Is there any valid case for that?
        duration_ms = actual_duration_ms or estimated_duration_ms or 0

        segment = Segment(
            format_id=media_header.format_id,
            is_init_segment=is_init_segment,
            duration_ms=duration_ms,
            start_data_range=media_header.start_data_range,
            sequence_number=sequence_number,
            content_length=media_header.content_length,
            start_ms=start_ms,
            initialized_format=initialized_format,
            duration_estimated=not actual_duration_ms,
            discard=discard
        )

        self._header_ids[media_header.header_id] = segment

        self.write_sabr_debug(f'Initialized Media Header {media_header.header_id} for sequence {sequence_number} (init_segment={is_init_segment}, discard={discard})', part=part)

    def process_media(self, part: UMPPart):
        header_id = part.data[0]
        segment = self._header_ids.get(header_id)
        if not segment:
            self.write_sabr_debug(f'Header ID {header_id} not found')
            return

        # Will count discarded (ignored) media as a request with data... as something is at least coming through
        self._request_had_data = True

        # Store the data in the segment, which we will yield later when we have received all parts for the segment
        segment.data += part.data[1:]

    def process_media_end(self, part: UMPPart):
        header_id = part.data[0]
        self.write_sabr_debug(f'Header ID: {header_id}', part=part)
        segment: Segment = self._header_ids.pop(header_id, None)

        if not segment:
            self.write_sabr_debug(f'Received a MediaEnd for an unknown or already finished header ID {header_id}', part=part)
            return

        self.write_sabr_debug(f'MediaEnd for {segment.format_id} (sequence {segment.sequence_number}, data length = {len(segment.data)})', part=part)

        if segment.content_length is not None and len(segment.data) != segment.content_length:
            raise SabrStreamError(
                f'Content length mismatch for {segment.format_id} (sequence {segment.sequence_number}): '
                f'expected {segment.content_length}, got {len(segment.data)}'
            )

        # Return the segment here because:
        # 1. We can validate that we received the correct data length
        # 2. In the case of a retry during segment media, the partial data is not sent to the caller
        if not segment.discard:
            # TODO: should we yield before or after processing the segment?
            yield MediaSegmentSabrPart(
                format_selector=segment.initialized_format.format_selector,
                format_id=segment.format_id,
                player_time_ms=self._client_abr_state.player_time_ms,
                fragment_index=segment.sequence_number,
                fragment_count=segment.initialized_format.total_sequences,
                data=segment.data,
                start_bytes=segment.start_data_range,
                is_init_segment=segment.is_init_segment
            )
        else:
            self.write_sabr_debug(f'Discarding media for {segment.initialized_format.format_id}', part=part)

        if segment.is_init_segment:
            segment.initialized_format.init_segment = segment
            # Do not create a buffered range for init segments
            return

        segment.initialized_format.current_segment = segment

        # Try to find a buffered range for this segment in sequence
        buffered_range = next(
            (br for br in segment.initialized_format.buffered_ranges if br.end_segment_index == segment.sequence_number - 1),
            None
        )

        if not buffered_range and any(
            br.start_segment_index <= segment.sequence_number <= br.end_segment_index
            for br in segment.initialized_format.buffered_ranges
        ):
            # Segment is already buffered, do not create a new buffered range. It was probably discarded.
            # This can be expected to happen in the case of video-only, where we discard the audio track (and mark it as entirely buffered)
            # We still want to create/update buffered range for discarded media IF it is not already buffered
            self.write_sabr_debug(f'Segment {segment.sequence_number} already buffered, not creating or updating buffered range (discard={segment.discard})', part=part)
            return


        if not buffered_range:
            # Create a new buffered range
            segment.initialized_format.buffered_ranges.append(BufferedRange(
                format_id=segment.initialized_format.format_id,
                start_time_ms=segment.start_ms,
                duration_ms=segment.duration_ms,
                start_segment_index=segment.sequence_number,
                end_segment_index=segment.sequence_number,
                time_range=TimeRange(
                    start_ticks=segment.start_ms,
                    duration_ticks=segment.duration_ms,
                    timescale=1000  # ms
                )
            ))
            self.write_sabr_debug(
                part=part, message=f'Created new buffered range for {segment.initialized_format.format_id} {segment.initialized_format.buffered_ranges[-1]}')
            return

        buffered_range.end_segment_index = segment.sequence_number
        if not self._live_metadata or not segment.duration_estimated:
            # We need to increment both duration_ms and time_range.duration
            buffered_range.duration_ms += segment.duration_ms
            if buffered_range.time_range.timescale != 1000:
                raise SabrStreamError(f'Buffered range timescale bad: {buffered_range.time_range.timescale} != 1000')
            buffered_range.time_range.duration_ticks += segment.duration_ms
        else:
            # Attempt to keep in sync with livestream, as the segment duration target is not always perfect.
            # The server seems to care more about the segment index than the duration.
            if buffered_range.start_time_ms > segment.start_ms:
                raise SabrStreamError(f'Buffered range start time mismatch: {buffered_range.start_time_ms} > {segment.start_ms}')

            new_duration = (segment.start_ms - buffered_range.start_time_ms) + segment.duration_ms
            buffered_range.duration_ms = buffered_range.time_range.duration_ticks = new_duration

    def process_live_metadata(self, part: UMPPart):
        self._live_metadata = protobug.loads(part.data, LiveMetadata)
        self.write_sabr_debug(part=part, protobug_obj=self._live_metadata, data=part.data)
        if self._live_metadata.head_sequence_time_ms:
            self._total_duration_ms = self._live_metadata.head_sequence_time_ms

        # If we have a head sequence number, we need to update the total sequences for each initialized format
        # For livestreams, it is not available in the format initialization metadata
        if self._live_metadata.head_sequence_number:
            for izf in self._initialized_formats.values():
                izf.total_sequences = self._live_metadata.head_sequence_number

    def process_stream_protection_status(self, part: UMPPart):
        sps = protobug.loads(part.data, StreamProtectionStatus)
        self.write_sabr_debug(f'Status: {StreamProtectionStatus.Status(sps.status).name}. SPS Retry: {self._sps_retry_count}', protobug_obj=sps, part=part, data=part.data)
        if sps.status == StreamProtectionStatus.Status.OK:
            self._sps_retry_count = 0
            if self.po_token:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.OK)
            else:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.NOT_REQUIRED)
        elif sps.status == StreamProtectionStatus.Status.ATTESTATION_PENDING:
            if sps.max_retries is not None:
                # Should not happen
                self._logger.warning(f'StreamProtectionStatus: Attestation Pending has a retry count of {sps.max_retries}{bug_reports_message()}')
            if self.po_token:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.PENDING)
            else:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.PENDING_MISSING)
        elif sps.status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED:
            if self._sps_retry_count >= (sps.max_retries or self._default_max_sps_retries):
                raise SabrStreamError(f'StreamProtectionStatus: Attestation Required ({"Invalid" if self.po_token else "Missing"} PO Token)')

            # xxx: temporal network error retries, host changes due to errors will count towards the SPS retry
            self._sps_retry_count += 1
            self._is_retry = True

            if self.po_token:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.INVALID)
            else:
                yield PoTokenStatusSabrPart(status=PoTokenStatusSabrPart.PoTokenStatus.MISSING)

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
        raise SabrStreamError('Unable to find a working Google Video Server. Is your connection okay?')

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

        if str(fmt_init_metadata.format_id) in self._initialized_formats:
            self.write_sabr_debug('Format already initialized', part)
            return

        format_selector = self._match_format_selector(fmt_init_metadata)
        if not format_selector:
            # Should not happen. If we ignored the format the server may refuse to send us any more data
            raise SabrStreamError(f'Received format {fmt_init_metadata.format_id} but it does not match any format selector')

        # Guard: Check if the format selector is already in use by another initialized format.
        # This can happen when the server changes the format to use (e.g. changing quality).
        #
        # Changing a format will require adding some logic to handle inactive formats.
        # Given we only provide one FormatId currently, and this should not occur in this case,
        # we will mark this as not currently supported and bail.
        for izf in self._initialized_formats.values():
            if izf.format_selector is format_selector:
                raise SabrStreamError('Server changed format. Changing formats is not currently supported')

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
            discard=format_selector.discard_media,
        )
        self._total_duration_ms = max(self._total_duration_ms or 0, fmt_init_metadata.end_time_ms or 0, duration_ms or 0)

        if initialized_format.discard:
            # Mark the entire format as buffered into oblivion if we plan to discard all media.
            # This stops the server sending us any more data for this format.
            # Note: Using JS_MAX_SAFE_INTEGER but could use any maximum value as long as the server accepts it.
            initialized_format.buffered_ranges = [BufferedRange(
                format_id=fmt_init_metadata.format_id,
                start_time_ms=0,
                duration_ms=JS_MAX_SAFE_INTEGER,
                start_segment_index=0,
                end_segment_index=JS_MAX_SAFE_INTEGER,
                time_range=TimeRange(
                    start_ticks=0,
                    duration_ticks=JS_MAX_SAFE_INTEGER,
                    timescale=1000
                )
            )]

        self._initialized_formats[str(fmt_init_metadata.format_id)] = initialized_format
        self.write_sabr_debug(f'Initialized Format: {initialized_format}', part=part)

    def process_next_request_policy(self, part: UMPPart):
        self._next_request_policy = protobug.loads(part.data, NextRequestPolicy)
        self.write_sabr_debug(part=part, protobug_obj=self._next_request_policy, data=part.data)

    def process_sabr_seek(self, part: UMPPart):
        sabr_seek = protobug.loads(part.data, SabrSeek)
        seek_to = math.ceil((sabr_seek.seek_time / sabr_seek.timescale) * 1000)
        self.write_sabr_debug(part=part, protobug_obj=sabr_seek, data=part.data)
        self.write_sabr_debug(f'Seeking to {seek_to}ms')
        self._client_abr_state.player_time_ms = seek_to

        # Clear latest segment as will no longer be in order
        for initialized_format in self._initialized_formats.values():
            initialized_format.current_segment = None
            yield MediaSeekSabrPart(
                reason=MediaSeekSabrPart.Reason.SERVER_SEEK,
                format_id=initialized_format.format_id,
                format_selector=initialized_format.format_selector,
            )

    def process_sabr_error(self, part: UMPPart):
        sabr_error = protobug.loads(part.data, SabrError)
        self.write_sabr_debug(part=part, protobug_obj=sabr_error, data=part.data)
        raise SabrStreamError(f'SABR Returned Error: {sabr_error}')

    def process_expiry(self):
        expires_at = int_or_none(traverse_obj(parse_qs(self.server_abr_streaming_url), ('expire', 0), get_all=False))

        if not expires_at:
            self.write_sabr_debug('No expiry found in SABR streaming URL. Will not be able to refresh.')
            return

        if expires_at - 300 >= time.time():
            self.write_sabr_debug(f'SABR streaming url expires in {int(expires_at - time.time())} seconds')
            return

        self.write_sabr_debug('Requesting player response refresh as SABR streaming URL is due to expire in 300 seconds')
        yield RefreshPlayerResponseSabrPart(reason=RefreshPlayerResponseSabrPart.Reason.SABR_URL_EXPIRY)


def get_br_chain(start_buffered_range: BufferedRange, buffered_ranges: List[BufferedRange]) -> List[BufferedRange]:
    # TODO: test
    # Return the continuous buffered range chain starting from the given buffered range
    # Note: It is assumed a segment is only present in one buffered range - it should not be allowed in multiple (by process media header)
    chain = [start_buffered_range]
    for br in sorted(buffered_ranges, key=lambda br: br.start_segment_index):
        if br.start_segment_index == chain[-1].end_segment_index + 1:
            chain.append(br)
        elif br.start_segment_index > chain[-1].end_segment_index + 1:
            break
    return chain