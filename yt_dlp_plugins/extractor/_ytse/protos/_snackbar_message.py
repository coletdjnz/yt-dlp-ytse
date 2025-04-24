import typing
import protobug


@protobug.message
class SnackbarMessage:
    # Unsure on contents
    content: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
