import typing
import protobug


@protobug.message
class Item:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    min_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class RequestCancellationPolicy:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    items: list[Item] = protobug.field(2, default_factory=list)
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(3, default=None)