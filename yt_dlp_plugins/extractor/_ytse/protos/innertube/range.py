import typing
import protobug

@protobug.message
class Range:
    legacy_start: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    legacy_end: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    start: typing.Optional[protobug.Int64] = protobug.field(3, default=None)
    end: typing.Optional[protobug.Int64] = protobug.field(4, default=None)