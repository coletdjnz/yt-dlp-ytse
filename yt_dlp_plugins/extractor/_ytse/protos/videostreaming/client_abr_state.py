import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.innertube.network_metered_state import NetworkMeteredState
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.media_capabilities import MediaCapabilities
from yt_dlp_plugins.extractor._ytse.protos.innertube.audio_quality import AudioQuality
from yt_dlp_plugins.extractor._ytse.protos.innertube.audio_route_output import AudioRouteOutputType
from yt_dlp_plugins.extractor._ytse.protos.innertube.detailed_network_type import DetailedNetworkType
from yt_dlp_plugins.extractor._ytse.protos.innertube.drm_track_type import DrmTrackType
from yt_dlp_plugins.extractor._ytse.protos.innertube.video_quality_setting import VideoQualitySetting



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
    client_viewport_is_flexible: typing.Optional[protobug.Int32] = protobug.field(22, default=None)
    bandwidth_estimate: typing.Optional[protobug.Int32] = protobug.field(23, default=None)
    min_audio_quality: typing.Optional[AudioQuality] = protobug.field(24, default=None)
    max_audio_quality: typing.Optional[AudioQuality] = protobug.field(25, default=None)
    video_quality_setting: typing.Optional[VideoQualitySetting] = protobug.field(26, default=None)
    audio_route: typing.Optional[AudioRouteOutputType] = protobug.field(27, default=None)
    player_time_ms: typing.Optional[protobug.Int64] = protobug.field(28, default=None)
    time_since_last_seek: typing.Optional[protobug.Int64] = protobug.field(29, default=None)
    data_saver_mode: typing.Optional[protobug.Int32] = protobug.field(30, default=None)  # seen on android = 0, todo: enum or bool? or low_power_mode
    network_metered_state: typing.Optional[NetworkMeteredState] = protobug.field(32, default=None)
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
    authorized_drm_track_types: typing.Optional[DrmTrackType] = protobug.field(55, default=None)
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
    audio_track_id: typing.Optional[protobug.String] = protobug.field(69, default=None)
     #unknown_field_70: typing.Optional[protobug.Bytes] = protobug.field(70, default=None)  # message or enum of some sort
    unknown_field_71: typing.Optional[protobug.Int32] = protobug.field(71, default=None)  # may be a bool
    unknown_field_72: typing.Optional[protobug.Bytes] = protobug.field(72, default=None)
    unknown_field_73: typing.Optional[AudioQuality] = protobug.field(73, default=None)

    unknown_field_77: typing.Optional[protobug.Int32] = protobug.field(77, default=None)