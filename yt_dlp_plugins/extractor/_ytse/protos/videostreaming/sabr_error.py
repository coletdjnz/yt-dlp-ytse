import typing
import protobug


@protobug.message
class Error:
    status_code: typing.Optional[protobug.Int32] = protobug.field(1, default=None)  # e.g. 403
    # enum of type? Seen = 4 when sabr.malformed_config, so could also point to the field
    type: typing.Optional[protobug.Int32] = protobug.field(4, default=None)


@protobug.message
class SabrError:
    type: typing.Optional[protobug.String] = protobug.field(1, default=None)
    action: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    error: typing.Optional[Error] = protobug.field(3, default=None)
