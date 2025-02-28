import typing
import protobug
from ._media_capabilities import MediaCapabilities


class DetailedNetworkType(protobug.Enum, strict=False):
    DETAILED_NETWORK_TYPE_UNKNOWN = 0
    DETAILED_NETWORK_TYPE_EDGE = 101
    DETAILED_NETWORK_TYPE_GPRS = 102
    DETAILED_NETWORK_TYPE_1_X_RTT = 103
    DETAILED_NETWORK_TYPE_CDMA = 104
    DETAILED_NETWORK_TYPE_EVDO_0 = 105
    DETAILED_NETWORK_TYPE_EVDO_A = 106
    DETAILED_NETWORK_TYPE_HSDPA = 107
    DETAILED_NETWORK_TYPE_HSPA = 108
    DETAILED_NETWORK_TYPE_HSUPA = 109
    DETAILED_NETWORK_TYPE_IDEN = 110
    DETAILED_NETWORK_TYPE_UMTS = 111
    DETAILED_NETWORK_TYPE_EVDO_B = 112
    DETAILED_NETWORK_TYPE_EHRPD = 113
    DETAILED_NETWORK_TYPE_HSPAP = 114
    DETAILED_NETWORK_TYPE_LTE = 115
    DETAILED_NETWORK_TYPE_WIFI = 116
    DETAILED_NETWORK_TYPE_BLUETOOTH = 117
    DETAILED_NETWORK_TYPE_ETHERNET = 118
    DETAILED_NETWORK_TYPE_WIMAX = 119
    DETAILED_NETWORK_TYPE_MOBILE_UNKNOWN = 120
    DETAILED_NETWORK_TYPE_NON_MOBILE_UNKNOWN = 121
    DETAILED_NETWORK_TYPE_DISCONNECTED = 122
    DETAILED_NETWORK_TYPE_APP_WIFI_HOTSPOT = 123
    DETAILED_NETWORK_TYPE_INTERNAL_WIFI_IMPAIRED = 124
    DETAILED_NETWORK_TYPE_NR_SA = 125
    DETAILED_NETWORK_TYPE_NR_NSA = 126


class AudioQuality(protobug.Enum, strict=False):
    AUDIO_QUALITY_UNKNOWN = 0
    AUDIO_QUALITY_ULTRALOW = 5
    AUDIO_QUALITY_LOW = 10
    AUDIO_QUALITY_MEDIUM = 20
    AUDIO_QUALITY_HIGH = 30


class VideoQualitySetting(protobug.Enum, strict=False):
    VIDEO_QUALITY_SETTING_UNKNOWN = 0
    VIDEO_QUALITY_SETTING_HIGHER_QUALITY = 1
    VIDEO_QUALITY_SETTING_DATA_SAVER = 2
    VIDEO_QUALITY_SETTING_ADVANCED_MENU = 3


class AudioRouteOutputType(protobug.Enum, strict=False):
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_UNKNOWN = 0
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_LINE_OUT = 1
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_HEADPHONES = 2
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_BLUETOOTH_A2DP = 3
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_BUILT_IN_RECEIVER = 4
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_BUILT_IN_SPEAKER = 5
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_HDMI = 6
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_AIR_PLAY = 7
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_BLUETOOTH_LE = 8
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_BLUETOOTH_HFP = 9
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_USB_AUDIO = 10
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_CAR_PLAY = 11
    PLAYBACK_AUDIO_ROUTE_OUTPUT_TYPE_ANDROID_AUDIO = 12


class NetworkMeteredState(protobug.Enum, strict=False):
    NETWORK_METERED_STATE_UNKNOWN = 0
    NETWORK_METERED_STATE_UNMETERED = 1
    NETWORK_METERED_STATE_METERED = 2


@protobug.message
class ClientAbrState:
    time_since_last_manual_format_selection_ms: typing.Optional[protobug.Int32] = protobug.field(13, default=None)
    last_manual_direction: typing.Optional[protobug.Int32] = protobug.field(14, default=None)
    last_manual_selected_resolution: typing.Optional[protobug.Int32] = protobug.field(16, default=None)
    detailed_network_type: typing.Optional[DetailedNetworkType] = protobug.field(17, default=None)
    client_viewport_width: typing.Optional[protobug.Int32] = protobug.field(18, default=None)
    client_viewport_height: typing.Optional[protobug.Int32] = protobug.field(19, default=None)
    client_bitrate_cap: typing.Optional[protobug.Int64] = protobug.field(20, default=None)
    sticky_resolution: typing.Optional[protobug.Int32] = protobug.field(21, default=None)
    client_viewport_is_flexible: typing.Optional[protobug.Int32] = protobug.field(22, default=None)  # seen on android = 1 (when playing audio+video only)
    bandwidth_estimate: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
    min_audio_quality: typing.Optional[AudioQuality] = protobug.field(24, default=None)
    max_audio_quality: typing.Optional[AudioQuality] = protobug.field(25, default=None)
    video_quality_setting: typing.Optional[VideoQualitySetting] = protobug.field(26, default=None)  # seen on android = 0
    audio_route: typing.Optional[AudioRouteOutputType] = protobug.field(27, default=None)  # seen on android = 5
    player_time_ms: typing.Optional[protobug.Int64] = protobug.field(28, default=None)
    time_since_last_seek: typing.Optional[protobug.Int64] = protobug.field(29, default=None)
    data_saver_mode: typing.Optional[protobug.Int32] = protobug.field(30, default=None)  # seen on android = 0, todo: enum or bool?
    network_metered_state: typing.Optional[NetworkMeteredState] = protobug.field(32, default=None)  # seen on android = 0
    visibility: typing.Optional[protobug.Int32] = protobug.field(34, default=None)
    playback_rate: typing.Optional[protobug.Float] = protobug.field(35, default=None)
    elapsed_wall_time_ms: typing.Optional[protobug.Int64] = protobug.field(36, default=None)
    media_capabilities: typing.Optional[MediaCapabilities] = protobug.field(38, default=None)
    time_since_last_action_ms: typing.Optional[protobug.Int64] = protobug.field(39, default=None)
    enabled_track_types_bitfield: typing.Optional[protobug.Int32] = protobug.field(40, default=None)
    max_pacing_rate: typing.Optional[protobug.Int32] = protobug.field(41, default=None)
    player_state: typing.Optional[protobug.Int64] = protobug.field(44, default=None)
    drc_enabled: typing.Optional[protobug.Bool] = protobug.field(46, default=None)
    unknown_field_48: typing.Optional[protobug.Int32] = protobug.field(48, default=None)
    unknown_field_50: typing.Optional[protobug.Int32] = protobug.field(50, default=None)
    unknown_field_51: typing.Optional[protobug.Int32] = protobug.field(51, default=None)
    sabr_report_request_cancellation_info: typing.Optional[protobug.Int32] = protobug.field(54, default=None)
    unknown_field_55: typing.Optional[protobug.Bytes] = protobug.field(55, default=None)  # some sort of message
    unknown_field_56: typing.Optional[protobug.Bool] = protobug.field(56, default=None)
    unknown_field_57: typing.Optional[protobug.Int64] = protobug.field(57, default=None)
    prefer_vp9: typing.Optional[protobug.Bool] = protobug.field(58, default=None)
    unknown_field_59: typing.Optional[protobug.Int32] = protobug.field(59, default=None)
    unknown_field_60: typing.Optional[protobug.Int32] = protobug.field(60, default=None)
    is_prefetch: typing.Optional[protobug.Bool] = protobug.field(61, default=None)
    sabr_support_quality_constraints: typing.Optional[protobug.Int32] = protobug.field(62, default=None)
    sabr_license_constraint: typing.Optional[protobug.Bytes] = protobug.field(63, default=None)
    allow_proxima_live_latency: typing.Optional[protobug.Int32] = protobug.field(64, default=None)
    sabr_force_proxima: typing.Optional[protobug.Int32] = protobug.field(66, default=None)
    unknown_field_67: typing.Optional[protobug.Int32] = protobug.field(67, default=None)
    sabr_force_max_network_interruption_duration_ms: typing.Optional[protobug.Int64] = protobug.field(68, default=None)
