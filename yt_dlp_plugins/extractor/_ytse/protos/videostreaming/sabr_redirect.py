import typing
import protobug


@protobug.message
class SabrRedirect:
    redirect_url: typing.Optional[protobug.String] = protobug.field(1, default=None)
