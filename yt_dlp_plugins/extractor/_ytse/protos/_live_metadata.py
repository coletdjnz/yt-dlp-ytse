import typing
import protobug


@protobug.message
class LiveMetadata:
    latest_sequence_number: typing.Optional[protobug.UInt32] = protobug.field(3, default=None)
    latest_sequence_duration_ms: typing.Optional[protobug.UInt64] = protobug.field(4, default=None)

    timestamp: typing.Optional[protobug.UInt64] = protobug.field(5, default=None)
    unknown_field_10: typing.Optional[protobug.UInt32] = protobug.field(10, default=None)  # maybe live status?

    dvr_start_duration: typing.Optional[protobug.UInt64] = protobug.field(12, default=None)  # earliest you can rewind the livestream
    dvr_start_timescale: typing.Optional[protobug.UInt32] = protobug.field(13, default=None)

    live_start_duration: typing.Optional[protobug.UInt64] = protobug.field(14, default=None)  # where SABR seek puts you to start streaming live?
    live_start_timescale: typing.Optional[protobug.UInt32] = protobug.field(15, default=None)

