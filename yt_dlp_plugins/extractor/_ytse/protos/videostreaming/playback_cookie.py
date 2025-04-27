import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId


@protobug.message
class PlaybackCookie:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    unknown_field_3: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    unknown_field_6: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    video_format: typing.Optional[FormatId] = protobug.field(7, default=None)
    audio_format: typing.Optional[FormatId] = protobug.field(8, default=None)
    unknown_field_14: typing.Optional[protobug.Int32] = protobug.field(14, default=None)
    unknown_field_20: typing.Optional[protobug.Bytes] = protobug.field(20, default=None)
    unknown_field_25: typing.Optional[protobug.Int32] = protobug.field(25, default=None)  # seen on ios = 1
