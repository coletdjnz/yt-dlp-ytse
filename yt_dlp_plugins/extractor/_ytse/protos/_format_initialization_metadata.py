import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos._format_id import FormatId

@protobug.message
class InitRange:
    start: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    end: typing.Optional[protobug.Int32] = protobug.field(2, default=None)


@protobug.message
class IndexRange:
    start: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    end: typing.Optional[protobug.Int32] = protobug.field(2, default=None)


@protobug.message
class FormatInitializationMetadata:
    video_id: protobug.String = protobug.field(1, default=None)
    format_id: FormatId = protobug.field(2, default=None)
    end_time_ms: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    field4: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    mime_type: typing.Optional[protobug.String] = protobug.field(5, default=None)
    init_range: typing.Optional[InitRange] = protobug.field(6, default=None)
    index_range: typing.Optional[IndexRange] = protobug.field(7, default=None)
    field8: typing.Optional[protobug.Int32] = protobug.field(8, default=None)
    duration_ms: typing.Optional[protobug.Int32] = protobug.field(9, default=None)
    field10: typing.Optional[protobug.Int32] = protobug.field(10, default=None)