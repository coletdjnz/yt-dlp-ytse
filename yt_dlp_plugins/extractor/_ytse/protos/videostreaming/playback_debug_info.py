import typing
import protobug

from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId

@protobug.message
class DebugInfo:
    label: typing.Optional[protobug.String] = protobug.field(1, default=None)
    text: typing.Optional[protobug.String] = protobug.field(2, default=None)

@protobug.message
class UnknownMessage1:
    video_id: typing.Optional[protobug.String] = protobug.field(1, default=None)
    format_id: typing.Optional[FormatId] = protobug.field(2, default=None)
    debug_info: typing.Optional[protobug.String] = protobug.field(3, default=None)

@protobug.message
class UnknownMessage2:
    # messages?
    unknown_field_1: list[UnknownMessage1] = protobug.field(1, default_factory=list)


@protobug.message
class PlaybackDebugInfo:
    unknown_field_1: typing.Optional[UnknownMessage2] = protobug.field(1, default=None)
