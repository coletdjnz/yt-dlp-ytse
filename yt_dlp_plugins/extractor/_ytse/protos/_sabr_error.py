import typing
import protobug


@protobug.message
class Error:
    status_code: typing.Optional[protobug.Int32] = protobug.field(1, default=None)  # e.g. 403


@protobug.message
class SabrError:
    type: typing.Optional[protobug.String] = protobug.field(1, default=None)
    code: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    errors: typing.Optional[Error] = protobug.field(3, default=None)
