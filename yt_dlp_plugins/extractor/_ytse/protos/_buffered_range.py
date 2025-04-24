import typing
import protobug
from ._format_id import FormatId
from ._time_range import TimeRange


@protobug.message
class Pa:
    video_id: typing.Optional[protobug.String] = protobug.field(1, default=None)
    lmt: typing.Optional[protobug.Int64] = protobug.field(2, default=None)


@protobug.message
class Kob:
    EW: list[Pa] = protobug.field(1, default_factory=list)


@protobug.message
class YPa:
    field1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    field2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    field3: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class BufferedRange:
    format_id: typing.Optional[FormatId] = protobug.field(1, default=None)
    start_time_ms: typing.Optional[protobug.Int64] = protobug.field(2, default=None)
    duration_ms: typing.Optional[protobug.Int64] = protobug.field(3, default=None)
    start_segment_index: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    end_segment_index: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(6, default=None)
    unknown_field_7: typing.Optional[protobug.Bytes] = protobug.field(7, default=None)  # some sort of message
    unknown_field_9: typing.Optional[Kob] = protobug.field(9, default=None)
    unknown_field_11: typing.Optional[YPa] = protobug.field(11, default=None)
    unknown_field_12: typing.Optional[YPa] = protobug.field(12, default=None)

