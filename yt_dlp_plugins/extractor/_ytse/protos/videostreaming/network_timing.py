import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.time_range import TimeRange

# b95b0e7a

@protobug.message
class sMA:
    type: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    event: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    wX: typing.Optional[protobug.Double] = protobug.field(3, default=None)
    fD: typing.Optional[protobug.Double] = protobug.field(4, default=None)
    CS: typing.Optional[protobug.String] = protobug.field(5, default=None)
    identifier: typing.Optional[protobug.String] = protobug.field(6, default=None)
    # field 7, 8 seen as 0
    qN: typing.Optional[protobug.Int32] = protobug.field(9, default=None)



@protobug.message
class Pp:
    uM: typing.Optional[sMA] = protobug.field(1, default=None)
    track_type: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    hN: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(4, default=None)
    tile_context: typing.Optional[protobug.String] = protobug.field(5, default=None)

@protobug.message
class NetworkTiming:
    network_timing: list[Pp] = protobug.field(1, default_factory=list)