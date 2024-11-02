import typing
import protobug

@protobug.message
class Item:
    fR: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    NK: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    minReadaheadMs: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class RequestCancellationPolicy:
    N0: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    items: list[Item] = protobug.field(2, default_factory=list)
    jq: typing.Optional[protobug.Int32] = protobug.field(3, default=None)