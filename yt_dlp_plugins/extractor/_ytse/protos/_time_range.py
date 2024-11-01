import typing
import protobug


@protobug.message
class TimeRange:
    start: typing.Optional[protobug.Int64] = protobug.field(1)
    duration: typing.Optional[protobug.Int64] = protobug.field(2)
    timescale: typing.Optional[protobug.Int32] = protobug.field(3)