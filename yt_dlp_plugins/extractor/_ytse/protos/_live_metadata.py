import typing
import protobug


@protobug.message
class LiveMetadata:
    latest_sequence_number: typing.Optional[protobug.UInt32] = protobug.field(3)
    latest_sequence_duration_ms: typing.Optional[protobug.UInt64] = protobug.field(4)

    timestamp: typing.Optional[protobug.UInt64] = protobug.field(5)
    target_duration_sec: typing.Optional[protobug.UInt32] = protobug.field(10)  # duration of each segment, in seconds

    segment_start_duration: typing.Optional[protobug.UInt64] = protobug.field(12)  # earliest you can rewind the livestream
    segment_start_timescale: typing.Optional[protobug.UInt32] = protobug.field(13)

    live_start_duration: typing.Optional[protobug.UInt64] = protobug.field(14)  # where SABR seek puts you to start streaming live?
    live_start_timescale: typing.Optional[protobug.UInt32] = protobug.field(15)

