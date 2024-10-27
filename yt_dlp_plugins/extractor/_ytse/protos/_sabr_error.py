import typing
import protobug


@protobug.message
class UnknownMessage:
    unknown_field: typing.Optional[protobug.Int32] = protobug.field(1, default=None)


@protobug.message
class SabrError:
    type: typing.Optional[protobug.String] = protobug.field(1, default=None)
    code: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    unknown_message: typing.Optional[UnknownMessage] = protobug.field(3, default=None)
