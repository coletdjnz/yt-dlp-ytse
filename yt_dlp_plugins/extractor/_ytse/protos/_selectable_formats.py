import typing
import protobug
from ._format_id import FormatId


@protobug.message
class UnknownNestedFormat:
    # unknown purpose
    format_id: typing.Optional[FormatId] = protobug.field(1, default=None)


@protobug.message
class SelectableFormats:
    selectable_video_formats: list[FormatId] = protobug.field(1, default_factory=list)
    selectable_audio_formats: list[FormatId] = protobug.field(2, default_factory=list)

    unknown_field_3: typing.Optional[protobug.String] = protobug.field(3, default=None)

    nested_selectable_video_formats: list[UnknownNestedFormat] = protobug.field(4, default_factory=list)
    nested_selectable_audio_formats: list[UnknownNestedFormat] = protobug.field(5, default_factory=list)