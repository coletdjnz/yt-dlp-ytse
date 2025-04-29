import typing
import protobug

from ._buffered_range import BufferedRange
from ._client_abr_state import ClientAbrState
from ._format_id import FormatId
from ._streamer_context import StreamerContext


@protobug.message
class Field4:
    field1: typing.Optional[protobug.Int32] = protobug.field(1)
    field2: typing.Optional[protobug.Int32] = protobug.field(2)
    field3: typing.Optional[protobug.Int32] = protobug.field(3)


@protobug.message
class Lo:
    format_id: FormatId = protobug.field(1)
    Lj: typing.Optional[protobug.Int32] = protobug.field(2)
    sequence_number: typing.Optional[protobug.Int32] = protobug.field(3)
    field4: Field4 = protobug.field(4)
    MZ: typing.Optional[protobug.Int32] = protobug.field(5)


@protobug.message
class OQa:
    field1: list[protobug.String] = protobug.field(1)
    field2: typing.Optional[protobug.Bytes] = protobug.field(2)
    field3: typing.Optional[protobug.String] = protobug.field(3)
    field4: typing.Optional[protobug.Int32] = protobug.field(4)
    field5: typing.Optional[protobug.Int32] = protobug.field(5)
    field6: typing.Optional[protobug.String] = protobug.field(6)


@protobug.message
class Pqa:
    formats: list[FormatId] = protobug.field(1)
    ud: list[BufferedRange] = protobug.field(2)
    clip_id: typing.Optional[protobug.String] = protobug.field(3)


@protobug.message
class VideoPlaybackAbrRequest:
    client_abr_state: ClientAbrState = protobug.field(1)
    selected_format_ids: list[FormatId] = protobug.field(2, default_factory=list)
    buffered_ranges: list[BufferedRange] = protobug.field(3, default_factory=list)
    player_time_ms: typing.Optional[protobug.Int64] = protobug.field(4, default=None)
    video_playback_ustreamer_config: typing.Optional[protobug.Bytes] = protobug.field(5, default=None)
   # lo: Lo = protobug.field(6, default=None)
    selected_audio_format_ids: list[FormatId] = protobug.field(16, default_factory=list)
    selected_video_format_ids: list[FormatId] = protobug.field(17, default_factory=list)
    streamer_context: StreamerContext = protobug.field(19, default_factory=StreamerContext)
 #   field21: OQa = protobug.field(21, default=None)
 #   field22: typing.Optional[protobug.Int32] = protobug.field(22, default=None)
 #   field23: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
 #   field1000: list[Pqa] = protobug.field(1000, default=None)