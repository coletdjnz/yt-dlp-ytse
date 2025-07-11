import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.innertube.compression_algorithm import CompressionAlgorithm
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.time_range import TimeRange


@protobug.message
class MediaHeader:
    header_id: typing.Optional[protobug.UInt32] = protobug.field(1, default=None)
    video_id: typing.Optional[protobug.String] = protobug.field(2, default=None)
    itag: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    last_modified: typing.Optional[protobug.UInt64] = protobug.field(4, default=None)
    xtags: typing.Optional[protobug.String] = protobug.field(5, default=None)
    start_data_range: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    compression: typing.Optional[CompressionAlgorithm] = protobug.field(7, default=None)
    is_init_segment: typing.Optional[protobug.Bool] = protobug.field(8, default=None)
    sequence_number: typing.Optional[protobug.Int64] = protobug.field(9, default=None)
    bitrate_bps: typing.Optional[protobug.Int64] = protobug.field(10, default=None)
    start_ms: typing.Optional[protobug.Int32] = protobug.field(11, default=None)
    duration_ms: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    format_id: typing.Optional[FormatId] = protobug.field(13, default=None)
    content_length: typing.Optional[protobug.Int64] = protobug.field(14, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(15, default=None)
    sequence_lmt: typing.Optional[protobug.Int32] = protobug.field(16, default=None)  # "sl". Matchs lmt%3D[INT] in m3u8 stream url
    unknown_field_17: typing.Optional[protobug.Int32] = protobug.field(17, default=None)  # seen = 17152, 65536
    unknown_field_19: typing.Optional[protobug.Int32] = protobug.field(19, default=None)  # seen on ios = 1
    clip_id: typing.Optional[protobug.String] = protobug.field(1000, default=None)