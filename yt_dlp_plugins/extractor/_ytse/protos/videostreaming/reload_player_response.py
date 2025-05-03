import typing
import protobug


@protobug.message
class ReloadPlaybackParams:
    token: typing.Optional[protobug.String] = protobug.field(1, default=None)


@protobug.message
class ReloadPlayerResponse:
    reload_playback_params: typing.Optional[ReloadPlaybackParams] = protobug.field(1, default=None)
