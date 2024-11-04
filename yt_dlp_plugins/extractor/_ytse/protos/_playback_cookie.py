import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId


@protobug.message
class PlaybackCookie:
    field1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    field2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    video_fmt: typing.Optional[FormatId] = protobug.field(7, default=None)
    audio_fmt: typing.Optional[FormatId] = protobug.field(8, default=None)