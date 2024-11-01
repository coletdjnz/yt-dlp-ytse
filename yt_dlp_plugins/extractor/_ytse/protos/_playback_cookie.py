import protobug
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId

"""
message PlaybackCookie {
  optional int32 field1 = 1; // Always 999999??
  optional int32 field2 = 2;
  optional .misc.FormatId video_fmt = 7;
  optional .misc.FormatId audio_fmt = 8;
}
"""


@protobug.message
class PlaybackCookie:
    field1: protobug.Int32 = protobug.field(1)
    field2: protobug.Int32 = protobug.field(2)
    video_fmt: FormatId = protobug.field(7)
    audio_fmt: FormatId = protobug.field(8)