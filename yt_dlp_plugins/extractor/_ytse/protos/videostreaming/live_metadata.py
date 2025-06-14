import typing
import protobug


@protobug.message
class LiveMetadata:
    broadcast_id: typing.Optional[protobug.String] = protobug.field(1, default=None)

    head_sequence_number: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    head_sequence_time_ms: typing.Optional[protobug.Int64] = protobug.field(4, default=None)
    wall_time_ms: typing.Optional[protobug.Int64] = protobug.field(5, default=None)
    video_id: typing.Optional[protobug.String] = protobug.field(6, default=None)
    source: typing.Optional[protobug.String] = protobug.field(7, default=None)  # seen = yt_live_broadcast.
    unknown_field_8: typing.Optional[protobug.Bytes] = protobug.field(8, default=None)  # post_live_dvr?

    unknown_field_10: typing.Optional[protobug.Int32] = protobug.field(10, default=None)  # Seen = 2
    unknown_field_11: typing.Optional[protobug.Int32] = protobug.field(11, default=None)  # seen = 4816
    # earliest you can rewind the livestream
    min_seekable_time_ticks: typing.Optional[protobug.Int64] = protobug.field(12, default=None)
    min_seekable_timescale: typing.Optional[protobug.Int32] = protobug.field(13, default=None)

    # where SABR seek puts you to start streaming live?
    max_seekable_time_ticks: typing.Optional[protobug.Int64] = protobug.field(14, default=None)
    max_seekable_timescale: typing.Optional[protobug.Int32] = protobug.field(15, default=None)
    unknown_field_16: typing.Optional[protobug.Int32] = protobug.field(16, default=None)

