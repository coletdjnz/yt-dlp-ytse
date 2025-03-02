import typing
import protobug

from ._buffered_range import BufferedRange
from ._client_abr_state import ClientAbrState
from ._format_id import FormatId
from ._streamer_context import StreamerContext


@protobug.message
class Field4:
    field1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    field2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    field3: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class Lo:
    format_id: typing.Optional[FormatId] = protobug.field(1, default=None)
    Lj: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    sequence_number: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    field4: typing.Optional[Field4] = protobug.field(4, default=None)
    MZ: typing.Optional[protobug.Int32] = protobug.field(5, default=None)


@protobug.message
class OQa:
    unknown_field_1: list[protobug.String] = protobug.field(1, default_factory=list)
    unknown_field_2: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)
    unknown_field_3: typing.Optional[protobug.String] = protobug.field(3, default=None)
    unknown_field_4: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    unknown_field_5: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    unknown_field_6: typing.Optional[protobug.String] = protobug.field(6, default=None)


@protobug.message
class Pqa:
    formats: list[FormatId] = protobug.field(1, default_factory=list)
    ud: list[BufferedRange] = protobug.field(2, default_factory=list)
    clip_id: typing.Optional[protobug.String] = protobug.field(3, default=None)


@protobug.message
class VideoPlaybackAbrRequest:
    client_abr_state: ClientAbrState = protobug.field(1)
    initialization_format_ids: list[FormatId] = protobug.field(2, default_factory=list)
    buffered_ranges: list[BufferedRange] = protobug.field(3, default_factory=list)
    player_time_ms: typing.Optional[protobug.Int64] = protobug.field(4, default=None)
    video_playback_ustreamer_config: typing.Optional[protobug.Bytes] = protobug.field(5, default=None)
    unknown_field_6: list[Lo] = protobug.field(6, default_factory=list)
    selected_audio_format_ids: list[FormatId] = protobug.field(16, default_factory=list)
    selected_video_format_ids: list[FormatId] = protobug.field(17, default_factory=list)
    selected_caption_format_ids: list[FormatId] = protobug.field(18, default_factory=list)  # unconfirmed name
    streamer_context: StreamerContext = protobug.field(19, default_factory=StreamerContext)
    unknown_field_21: typing.Optional[OQa] = protobug.field(21, default=None)
    unknown_field_22: typing.Optional[protobug.Int32] = protobug.field(22, default=None)
    unknown_field_23: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
    unknown_field_1000: list[Pqa] = protobug.field(1000, default_factory=list)
