import typing
import protobug


@protobug.message
class TimeRange:
    start: typing.Optional[protobug.Int64] = protobug.field(1, default=None)
    duration: typing.Optional[protobug.Int64] = protobug.field(2, default=None)
    timescale: typing.Optional[protobug.Int32] = protobug.field(3, default=None)