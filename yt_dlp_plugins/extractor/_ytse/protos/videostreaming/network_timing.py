import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.time_range import TimeRange

# b95b0e7a

class TrackType(protobug.Enum, strict=False):
    TRACK_TYPE_AUDIO = 1
    TRACK_TYPE_VIDEO = 2


@protobug.message
class UnknownMessage1:
    type: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    event: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    unknown_double_3: typing.Optional[protobug.Double] = protobug.field(3, default=None)
    unknown_double_4: typing.Optional[protobug.Double] = protobug.field(4, default=None)
    unknown_string_5: typing.Optional[protobug.String] = protobug.field(5, default=None)
    # also referred to as "cid"
    # if present, in the format VIDEO_ID;??;TIMESTAMP
    identifier: typing.Optional[protobug.String] = protobug.field(6, default=None)
    # field 7, 8 seen as 0
    unknown_int_9: typing.Optional[protobug.Int32] = protobug.field(9, default=None)



@protobug.message
class Timing:
    unknown_message_1: typing.Optional[UnknownMessage1] = protobug.field(1, default=None)
    track_type: typing.Optional[TrackType] = protobug.field(2, default=None)
    sequence_number: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(4, default=None)
    tile_context: typing.Optional[protobug.String] = protobug.field(5, default=None)

@protobug.message
class NetworkTiming:
    network_timing: list[Timing] = protobug.field(1, default_factory=list)