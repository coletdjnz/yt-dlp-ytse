import typing
import protobug

from yt_dlp_plugins.extractor._ytse.protos.videostreaming.buffered_range import BufferedRange
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.client_abr_state import ClientAbrState
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.streamer_context import StreamerContext


@protobug.message
class UnknownMessage1:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    unknown_field_3: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class UnknownMessage2:
    format_id: typing.Optional[FormatId] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    sequence_number: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    unknown_field_4: typing.Optional[UnknownMessage1] = protobug.field(4, default=None)
    unknown_field_5: typing.Optional[protobug.Int32] = protobug.field(5, default=None)


@protobug.message
class UnknownMessage3:
    unknown_field_1: list[protobug.String] = protobug.field(1, default_factory=list)
    unknown_field_2: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)
    unknown_field_3: typing.Optional[protobug.String] = protobug.field(3, default=None)
    unknown_field_4: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    unknown_field_5: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    unknown_field_6: typing.Optional[protobug.String] = protobug.field(6, default=None)


@protobug.message
class UnknownMessage4:
    formats: list[FormatId] = protobug.field(1, default_factory=list)
    ud: list[BufferedRange] = protobug.field(2, default_factory=list)
    clip_id: typing.Optional[protobug.String] = protobug.field(3, default=None)


@protobug.message
class VideoPlaybackAbrRequest:
    client_abr_state: ClientAbrState = protobug.field(1, default=None)
    initialized_format_ids: list[FormatId] = protobug.field(2, default_factory=list)
    buffered_ranges: list[BufferedRange] = protobug.field(3, default_factory=list)
    player_time_ms: typing.Optional[protobug.Int64] = protobug.field(4, default=None)
    video_playback_ustreamer_config: typing.Optional[protobug.Bytes] = protobug.field(5, default=None)
    unknown_field_6: list[UnknownMessage2] = protobug.field(6, default_factory=list)

    selected_audio_format_ids: list[FormatId] = protobug.field(16, default_factory=list)
    selected_video_format_ids: list[FormatId] = protobug.field(17, default_factory=list)
    selected_caption_format_ids: list[FormatId] = protobug.field(18, default_factory=list)  # unconfirmed name
    streamer_context: StreamerContext = protobug.field(19, default_factory=StreamerContext)

    unknown_field_21: typing.Optional[UnknownMessage3] = protobug.field(21, default=None)
    unknown_field_22: typing.Optional[protobug.Int32] = protobug.field(22, default=None)
    unknown_field_23: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
    unknown_field_1000: list[UnknownMessage4] = protobug.field(1000, default_factory=list)