import typing
import protobug
@protobug.message
class AudioTrack:
    display_name: typing.Optional[protobug.String] = protobug.field(4, default=None)
    id: typing.Optional[protobug.String] = protobug.field(5, default=None)
    audio_is_default: typing.Optional[protobug.Bool] = protobug.field(6, default=None)
    is_auto_dubbed: typing.Optional[protobug.Bool] = protobug.field(7, default=None)
