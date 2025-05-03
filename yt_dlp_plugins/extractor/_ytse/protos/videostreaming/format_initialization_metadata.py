import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.innertube.format_stream import FormatStream
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId
from yt_dlp_plugins.extractor._ytse.protos.innertube.range import Range


@protobug.message
class FormatInitializationMetadata:
    video_id: protobug.String = protobug.field(1, default=None)
    format_id: FormatId = protobug.field(2, default=None)
    end_time_ms: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    total_segments: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    mime_type: typing.Optional[protobug.String] = protobug.field(5, default=None)
    init_range: typing.Optional[Range] = protobug.field(6, default=None)
    index_range: typing.Optional[Range] = protobug.field(7, default=None)
    format: typing.Optional[FormatStream] = protobug.field(8, default=None)
    duration: typing.Optional[protobug.Int32] = protobug.field(9, default=None)
    duration_timescale: typing.Optional[protobug.Int32] = protobug.field(10, default=None)