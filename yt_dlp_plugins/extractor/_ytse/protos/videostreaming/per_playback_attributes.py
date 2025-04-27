import typing
import protobug


@protobug.message
class PerPlaybackAttributes:
    itag_denylist: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
