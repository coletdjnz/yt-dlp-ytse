import typing
import protobug
from ._format_id import FormatId


@protobug.message
class PlaybackCookie:
    field1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    field2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    field3: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    field6: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    video_fmt: typing.Optional[FormatId] = protobug.field(7, default=None)
    audio_fmt: typing.Optional[FormatId] = protobug.field(8, default=None)
    field14: typing.Optional[protobug.Int32] = protobug.field(14, default=None)
    field20: typing.Optional[protobug.Bytes] = protobug.field(20, default=None)
