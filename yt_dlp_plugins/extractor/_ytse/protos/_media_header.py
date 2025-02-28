import typing
import protobug
from ._format_id import FormatId
from ._time_range import TimeRange


@protobug.message
class MediaHeader:
    class Compression(protobug.Enum, strict=False):
        COMPRESSION_ALGORITHM_UNKNOWN = 0
        COMPRESSION_ALGORITHM_NONE = 1
        COMPRESSION_ALGORITHM_GZIP = 2

        """
        may also match:
        COMPRESSION_FORMAT_UNKNOWN = 0
        COMPRESSION_FORMAT_IDENTITY = 1
        COMPRESSION_FORMAT_GZIP = 2
        COMPRESSION_FORMAT_BROTLI = 3?
        """

    header_id: typing.Optional[protobug.UInt32] = protobug.field(1, default=None)
    video_id: typing.Optional[protobug.String] = protobug.field(2, default=None)
    itag: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    last_modified: typing.Optional[protobug.UInt64] = protobug.field(4, default=None)
    xtags: typing.Optional[protobug.String] = protobug.field(5, default=None)
    start_data_range: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    compression: typing.Optional[Compression] = protobug.field(7, default=None)
    is_init_segment: typing.Optional[protobug.Bool] = protobug.field(8, default=None)
    sequence_number: typing.Optional[protobug.Int64] = protobug.field(9, default=None)
    unknown_field_10: typing.Optional[protobug.Int64] = protobug.field(10, default=None)
    start_ms: typing.Optional[protobug.Int32] = protobug.field(11, default=None)
    duration_ms: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    format_id: typing.Optional[FormatId] = protobug.field(13, default=None)
    content_length: typing.Optional[protobug.Int64] = protobug.field(14, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(15, default=None)
    timestamp: typing.Optional[protobug.Int32] = protobug.field(16, default=None)
    unknown_field_17: typing.Optional[protobug.Int32] = protobug.field(17, default=None)  # seen = 17152, 65536
    unknown_field_19: typing.Optional[protobug.Int32] = protobug.field(19, default=None)  # seen on ios = 1

