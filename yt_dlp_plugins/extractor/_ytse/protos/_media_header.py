import enum
import typing
import protobug


@protobug.message
class MediaHeader:
    class Compression(enum.IntEnum):
        UNKNOWN_VAL_0 = 0
        UNKNOWN_VAL_1 = 1
        GZIP = 2

    header_id: typing.Optional[protobug.UInt32] = protobug.field(1, default=None)
    video_id: typing.Optional[protobug.String] = protobug.field(2, default=None)
    itag: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    lmt: typing.Optional[protobug.UInt64] = protobug.field(4, default=None)
    xtags: typing.Optional[protobug.String] = protobug.field(5, default=None)
    start_data_range: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    compression: typing.Optional[Compression] = protobug.field(7, default=None)
    is_init_segment: typing.Optional[protobug.Bool] = protobug.field(8, default=None)
    sequence_number: typing.Optional[protobug.Int64] = protobug.field(9, default=None)
    unknown_field_10: typing.Optional[protobug.Int64] = protobug.field(10, default=None)
    start_ms: typing.Optional[protobug.Int32] = protobug.field(11, default=None)
    duration_ms: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    content_length: typing.Optional[protobug.Int64] = protobug.field(14, default=None)

