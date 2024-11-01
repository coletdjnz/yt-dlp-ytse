import enum
import typing
import protobug
from._media_capabilities import MediaCapabilities

"""
message ClientAbrState {
  optional int32 time_since_last_manual_format_selection_ms = 13;
  optional int32 last_manual_direction = 14;
  optional int32 quality = 16;
  optional int32 detailed_network_type = 17;
  optional int32 max_width = 18;
  optional int32 max_height = 19;
  optional int32 selected_quality_height = 21;
  optional int32 r7 = 23;
  optional int64 start_time_ms = 28;
  optional int64 time_since_last_seek = 29;
  optional int32 visibility = 34;
  optional int64 time_since_last_req = 36;
  optional MediaCapabilities media_capabilities = 38;
  optional int64 time_since_last_action = 39;
  // optional int32 Gw = 40;
  optional MediaType media_type = 40;
  optional int64 player_state = 44;
  optional bool range_compression = 46;
  optional int32 Jda = 48;
  optional int32 qw = 50;
  optional int32 Ky = 51;
  optional int32 sabr_report_request_cancellation_info = 54;
  optional bool l = 56;
  optional int64 G7 = 57;
  optional bool prefer_vp9 = 58;
  optional int32 qj = 59;
  optional int32 Hx = 60;
  optional bool is_prefetch = 61;
  optional int32 sabr_support_quality_constraints = 62;
  optional bytes sabr_license_constraint = 63;
  optional int32 allow_proxima_live_latency = 64;
  optional int32 sabr_force_proxima = 66;
  optional int32 Tqb = 67;
  optional int64 sabr_force_max_network_interruption_duration_ms = 68;
  optional float playback_rate = 285;

  enum MediaType {
    MEDIA_TYPE_DEFAULT = 0;
    MEDIA_TYPE_AUDIO = 1;
    MEDIA_TYPE_VIDEO = 2;
    USE_SERVER_FORMAT_FILTER = 3;
    UNKNOWN_4 = 4;
    UNKNOWN_5 = 5;
    UNKNOWN_6 = 6;
    UNKNOWN_7 = 7;
    UNKNOWN_8 = 8;
    UNKNOWN_9 = 9;
    UNKNOWN_10 = 10;
  }
}
"""

@protobug.message
class ClientAbrState:
    class MediaType(enum.IntEnum):
        MEDIA_TYPE_DEFAULT = 0
        MEDIA_TYPE_AUDIO = 1
        MEDIA_TYPE_VIDEO = 2
        USE_SERVER_FORMAT_FILTER = 3

    time_since_last_manual_format_selection_ms: typing.Optional[protobug.Int32] = protobug.field(13, default=None)
    last_manual_direction: typing.Optional[protobug.Int32] = protobug.field(14, default=None)
    quality: typing.Optional[protobug.Int32] = protobug.field(16, default=None)
    detailed_network_type: typing.Optional[protobug.Int32] = protobug.field(17, default=None)
    max_width: typing.Optional[protobug.Int32] = protobug.field(18, default=None)
    max_height: typing.Optional[protobug.Int32] = protobug.field(19, default=None)
    selected_quality_height: typing.Optional[protobug.Int32] = protobug.field(21, default=None)
    r7: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
    start_time_ms: typing.Optional[protobug.Int64] = protobug.field(28, default=None)
    time_since_last_seek: typing.Optional[protobug.Int64] = protobug.field(29, default=None)
    visibility: typing.Optional[protobug.Int32] = protobug.field(34, default=None)
    time_since_last_req: typing.Optional[protobug.Int64] = protobug.field(36, default=None)
    media_capabilities: typing.Optional[MediaCapabilities] = protobug.field(38, default=None)
    time_since_last_action: typing.Optional[protobug.Int64] = protobug.field(39, default=None)
    media_type: typing.Optional[MediaType] = protobug.field(40, default=None)
    player_state: typing.Optional[protobug.Int64] = protobug.field(44, default=None)
    range_compression: typing.Optional[protobug.Bool] = protobug.field(46, default=None)
    Jda: typing.Optional[protobug.Int32] = protobug.field(48, default=None)
    qw: typing.Optional[protobug.Int32] = protobug.field(50, default=None)
    Ky: typing.Optional[protobug.Int32] = protobug.field(51, default=None)
    sabr_report_request_cancellation_info: typing.Optional[protobug.Int32] = protobug.field(54, default=None)
    l: typing.Optional[protobug.Bool] = protobug.field(56, default=None)
    G7: typing.Optional[protobug.Int64] = protobug.field(57, default=None)
    prefer_vp9: typing.Optional[protobug.Bool] = protobug.field(58, default=None)
    qj: typing.Optional[protobug.Int32] = protobug.field(59, default=None)
    Hx: typing.Optional[protobug.Int32] = protobug.field(60, default=None)
    is_prefetch: typing.Optional[protobug.Bool] = protobug.field(61, default=None)
    sabr_support_quality_constraints: typing.Optional[protobug.Int32] = protobug.field(62, default=None)
    sabr_license_constraint: typing.Optional[protobug.Bytes] = protobug.field(63, default=None)
    allow_proxima_live_latency: typing.Optional[protobug.Int32] = protobug.field(64, default=None)
    sabr_force_proxima: typing.Optional[protobug.Int32] = protobug.field(66, default=None)
    Tqb: typing.Optional[protobug.Int32] = protobug.field(67, default=None)
    sabr_force_max_network_interruption_duration_ms: typing.Optional[protobug.Int64] = protobug.field(68, default=None)
    playback_rate: typing.Optional[protobug.Float] = protobug.field(285, default=None)
