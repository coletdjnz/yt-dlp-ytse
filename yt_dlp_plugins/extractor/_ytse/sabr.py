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


class FormatType(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'


@dataclasses.dataclass
class FormatRequest:
    format_type: FormatType
    format_id: FormatId
    quality: typing.Optional[str] = None
    height: typing.Optional[str] = None


class SabrStreamConsumedError(DownloadError):
    pass

@dataclasses.dataclass
class SabrPart:
    pass


@dataclasses.dataclass
class MediaSabrPart(SabrPart):
    requested_format: FormatRequest
    format_id: FormatId
    player_time_ms: int = 0
    start_bytes: int = 0
    fragment_index: int = None
    fragment_count: int = None
    is_init_fragment: bool = False
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
        video_formats: List[FormatRequest] = None, audio_formats: List[FormatRequest] = None,
        live_segment_target_duration_sec: int = None,
        reload_config_fn: typing.Callable[[], tuple[str, str]] = None,
        start_time_ms: int = 0,
        debug=False,
        po_token: str = None,
        http_retries: int = 3,
    ):

        self._logger = logger
        self._debug = debug
        self._urlopen = urlopen

        self.requested_video_formats: List[FormatRequest] = video_formats or []
        self.requested_audio_formats: List[FormatRequest] = audio_formats or []
        self.server_abr_streaming_url = server_abr_streaming_url
        self.video_playback_ustreamer_config = video_playback_ustreamer_config
        self.po_token = po_token
        self.reload_config_fn = reload_config_fn
        self.client_info = client_info
        self.live_segment_target_duration_sec = live_segment_target_duration_sec or 5
        self.start_time_ms = start_time_ms
        self.http_retries = http_retries

        if self.live_segment_target_duration_sec:
            self.write_sabr_debug(f'using live_segment_target_duration_sec: {self.live_segment_target_duration_sec}')

        # State management
        self._requests_no_data = 0
        self._request_number = 0

        self._sps_retry_count = 0
        self._is_retry = False
        self._default_max_sps_retries = 5

        self._redirected = False
        self._request_had_data = False
        self._sabr_seeked = False
        self._header_ids: dict[int, Sequence] = {}
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
        if len(self.requested_video_formats) == 0:
            enabled_track_types_bitfield = 1  # Audio only

        # todo: handle non-format-id format requests
        self._selected_audio_format_ids = [f.format_id for f in self.requested_audio_formats]
        self._selected_video_format_ids = [f.format_id for f in self.requested_video_formats]

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
                selectable_video_format_ids=self._selected_video_format_ids,
                selectable_audio_format_ids=self._selected_audio_format_ids,
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

            self._update_request_state()
            self._prepare_next_request()

        self._consumed = True

    def _update_request_state(self):
        if not self._request_had_data and not self._is_retry:
            # todo: how to prevent youtube sending us in a redirect loop?
            if self._requests_no_data >= 2 and not self._redirected:
                if self._total_duration_ms and self._client_abr_state.player_time_ms < self._total_duration_ms:
                    # todo: if not live, this should probably be a fatal error
                    # todo: test streams that go down temporary. Should we increase this?
                    # todo: for streams, check against live metadata latest segment time and watch if it increases
                    #  configure a "wait for end" stream var in seconds?
                    self._logger.warning('No data found in three consecutive requests - assuming end of video')
                    self._consumed = True  # stream finished?
            self._requests_no_data += 1
        else:
            self._requests_no_data = 0

        self._request_had_data = False

    def _prepare_next_request(self):
        if len(self._header_ids):
            self._logger.warning(f'Extraneous header IDs left: {list(self._header_ids.values())}')
            self._header_ids.clear()

        # Do not update client abr state if we are retrying
        # For the case we fail midway through a response after reading some media data, but didn't get all of it.
        if not self._is_retry:
            current_buffered_ranges = [initialized_format.buffered_ranges[-1] for initialized_format in self._initialized_formats.values() if initialized_format.buffered_ranges]

            # choose format that is the most behind
            lowest_buffered_range = min(current_buffered_ranges, key=lambda x: x.start_time_ms + x.duration_ms) if current_buffered_ranges else None
            min_buffered_duration_ms = lowest_buffered_range.start_time_ms + lowest_buffered_range.duration_ms if lowest_buffered_range else 0
            next_request_backoff_ms = (self._next_request_policy and self._next_request_policy.backoff_time_ms) or 0

            self._client_abr_state.player_time_ms = max(
                min_buffered_duration_ms,
                # next request policy backoff_time_ms is the minimum to increment player_time_ms by
                self._client_abr_state.player_time_ms + next_request_backoff_ms,
            )

            # Check if the latest segment is the last one of each format (if data is available)
            if not self._live_metadata and len(current_buffered_ranges) == len(self._initialized_formats):
                if all(
                    (
                        initialized_format.buffered_ranges
                        and initialized_format.buffered_ranges[-1].end_segment_index is not None
                        and initialized_format.total_sequences is not None
                        and initialized_format.buffered_ranges[-1].end_segment_index == initialized_format.total_sequences
                    )
                    for initialized_format in self._initialized_formats.values()
                ):
                    self.write_sabr_debug(f'Reached last segment for all formats, assuming end of media')
                    self._consumed = True

            # Check if we have exceeded the total duration of the media (if not live),
            #  or wait for the next segment (if live)
            # TODO: should consider live stream timestamp in LIVE_METADATA perhaps?
            if self._total_duration_ms and (self._client_abr_state.player_time_ms >= self._total_duration_ms):
                if self._live_metadata:
                    self._client_abr_state.player_time_ms = self._total_duration_ms
                    wait_time = next_request_backoff_ms + self.live_segment_target_duration_sec * 1000
                    self.write_sabr_debug(f'is live, sleeping {wait_time / 1000} seconds for next fragment')
                    time.sleep(wait_time / 1000)

                else:
                    self.write_sabr_debug(f'End of media (player time ms {self._client_abr_state.player_time_ms} >= total duration ms {self._total_duration_ms})')
                    self._consumed = True

            if not self._consumed:
                self.write_sabr_debug(f'Next request player time ms: {self._client_abr_state.player_time_ms}, total duration ms: {self._total_duration_ms}')

        self._next_request_policy = None
        self._sabr_seeked = False
        self._redirected = False
        self._is_retry = False

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

        estimated_duration_ms = self._live_metadata and self.live_segment_target_duration_sec * 1000

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

        self._header_ids[media_header.header_id] = initialized_format.sequences[sequence_number or 0]

        if not is_init_segment:
            current_buffered_range = initialized_format.buffered_ranges[-1] if initialized_format.buffered_ranges else None

            # todo: if we sabr seek, then we get two segments in same request, we end up creating two buffered ranges.
            # Perhaps we should have sabr_seeked as part of initialized_format?
            if not current_buffered_range or self._sabr_seeked:
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
                    part=part, message=f'Created new buffered range for {media_header.format_id} (sabr seeked={self._sabr_seeked}): {initialized_format.buffered_ranges[-1]}')
                return

            end_segment_index = current_buffered_range.end_segment_index or 0
            if end_segment_index != 0 and end_segment_index + 1 != sequence_number:
                raise DownloadError(f'End segment index mismatch: {end_segment_index + 1} != {sequence_number}. Buffered Range: {current_buffered_range}')

            current_buffered_range.end_segment_index = sequence_number

            if not self._live_metadata or actual_duration_ms:
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
        current_sequence = self._header_ids.get(header_id)
        if not current_sequence:
            self.write_sabr_debug(f'Header ID {header_id} not found', part=part)
            return

        initialized_format = current_sequence.initialized_format

        if not initialized_format:
            self.write_sabr_debug(f'Initialized Format not found for header ID {header_id}', part=part)
            return

        self._request_had_data = True

        return MediaSabrPart(
            requested_format=initialized_format.requested_format,
            format_id=current_sequence.format_id,
            player_time_ms=self._client_abr_state.player_time_ms,
            fragment_index=current_sequence.sequence_number,
            fragment_count=self._live_metadata and self._live_metadata.head_sequence_number,
            data=part.data[1:],
        )

    def process_media_end(self, part: UMPPart):
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

    def _find_matching_requested_format(self, format_init_metadata: FormatInitializationMetadata):
        for requested_format in self.requested_audio_formats + self.requested_video_formats:
            if requested_format.format_id:
                if (
                    requested_format.format_id.itag == format_init_metadata.format_id.itag
                    and requested_format.format_id.lmt == format_init_metadata.format_id.lmt
                    and requested_format.format_id.xtags == format_init_metadata.format_id.xtags
                ):
                    return requested_format
            else:
                # todo: add more matching criteria if the requested format does not have a format_id
                pass

    def process_format_initialization_metadata(self, part: UMPPart):
        fmt_init_metadata = protobug.loads(part.data, FormatInitializationMetadata)
        self.write_sabr_debug(part=part, protobug_obj=fmt_init_metadata, data=part.data)

        initialized_format_key = get_format_key(fmt_init_metadata.format_id)

        if initialized_format_key in self._initialized_formats:
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
            total_sequences=fmt_init_metadata.total_segments,
        )
        self._total_duration_ms = max(self._total_duration_ms or 0, fmt_init_metadata.end_time_ms or 0, duration_ms or 0)

        self._initialized_formats[get_format_key(fmt_init_metadata.format_id)] = initialized_format

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
        self._sabr_seeked = True

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
