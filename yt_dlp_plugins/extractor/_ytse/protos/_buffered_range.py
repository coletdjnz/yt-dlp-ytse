import typing
import protobug
from ._format_id import FormatId
from ._time_range import TimeRange


@protobug.message
class Pa:
    video_id: typing.Optional[protobug.String] = protobug.field(1)
    lmt: typing.Optional[protobug.UInt64] = protobug.field(2)


@protobug.message
class Kob:
    EW: list[Pa] = protobug.field(1)


@protobug.message
class YPa:
    field1: typing.Optional[protobug.Int32] = protobug.field(1)
    field2: typing.Optional[protobug.Int32] = protobug.field(2)
    field3: typing.Optional[protobug.Int32] = protobug.field(3)


@protobug.message
class BufferedRange:
    format_id: FormatId = protobug.field(1)
    start_time_ms: typing.Optional[protobug.Int64] = protobug.field(2, default=None)
    duration_ms: typing.Optional[protobug.Int64] = protobug.field(3, default=None)
    start_segment_index: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    end_segment_index: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    time_range: typing.Optional[TimeRange] = protobug.field(6, default=None)
    # field9: Kob = protobug.field(9)
    # field11: YPa = protobug.field(11)
    # field12: YPa = protobug.field(12)

