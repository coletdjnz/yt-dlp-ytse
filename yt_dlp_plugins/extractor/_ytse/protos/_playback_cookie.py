import protobug
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId


@protobug.message
class PlaybackCookie:
    field1: protobug.Int32 = protobug.field(1)
    field2: protobug.Int32 = protobug.field(2)
    video_fmt: FormatId = protobug.field(7)
    audio_fmt: FormatId = protobug.field(8)