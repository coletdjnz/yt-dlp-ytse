import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId


@protobug.message
class SelectableFormat:
    format_id: typing.Optional[FormatId] = protobug.field(1, default=None)


@protobug.message
class SelectableFormats:
    selectable_video_formats: list[FormatId] = protobug.field(1, default_factory=list)
    selectable_audio_formats: list[FormatId] = protobug.field(2, default_factory=list)

    unknown_field_3: typing.Optional[protobug.String] = protobug.field(3, default=None)

    selectable_video_format: list[SelectableFormat] = protobug.field(4, default_factory=list)
    selectable_audio_format: list[SelectableFormat] = protobug.field(5, default_factory=list)