import typing
import protobug

from ._format_id import FormatId

@protobug.message
class DebugInfo:
    label: typing.Optional[protobug.String] = protobug.field(1, default=None)
    text: typing.Optional[protobug.String] = protobug.field(2, default=None)

@protobug.message
class z9K:
    video_id: typing.Optional[protobug.String] = protobug.field(1, default=None)
    format_id: typing.Optional[FormatId] = protobug.field(2, default=None)
    debug_info: typing.Optional[protobug.String] = protobug.field(3, default=None)

@protobug.message
class H8o:
    # messages?
    n1: list[z9K] = protobug.field(1, default_factory=list)


@protobug.message
class PlaybackDebugInfo:
    mV: typing.Optional[H8o] = protobug.field(1, default=None)
