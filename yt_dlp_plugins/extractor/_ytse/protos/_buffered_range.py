import typing
import protobug
from ._format_id import FormatId
from ._time_range import TimeRange

"""
message BufferedRange {
  required .misc.FormatId format_id = 1;
  required int64 start_time_ms = 2;
  required int64 duration_ms = 3;
  required int32 start_segment_index = 4;
  required int32 end_segment_index = 5;
  optional TimeRange time_range = 6;
  optional Kob field9 = 9;
  optional YPa field11 = 11; 
  optional YPa field12 = 12;
}

message Kob {
  message Pa {
    optional string video_id = 1;
    optional uint64 lmt = 2;
  }
  repeated Pa EW = 1;
}

message YPa {
  optional int32 field1 = 1;
  optional int32 field2 = 2;
  optional int32 field3 = 3;
}

"""


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
    start_time_ms: protobug.Int64 = protobug.field(2)
    duration_ms: protobug.Int64 = protobug.field(3)
    start_segment_index: protobug.Int32 = protobug.field(4)
    end_segment_index: protobug.Int32 = protobug.field(5)
    time_range: TimeRange = protobug.field(6)
    field9: Kob = protobug.field(9)
    field11: YPa = protobug.field(11)
    field12: YPa = protobug.field(12)

