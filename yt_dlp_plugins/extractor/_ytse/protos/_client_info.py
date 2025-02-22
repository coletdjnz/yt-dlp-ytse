import typing
import protobug


class ClientFormFactor(protobug.Enum, strict=False):
    UNKNOWN_FORM_FACTOR = 0
    SMALL_FORM_FACTOR = 1
    LARGE_FORM_FACTOR = 2
    AUTOMOTIVE_FORM_FACTOR = 3
    WEARABLE_FORM_FACTOR = 4


@protobug.message
class GLDeviceInfo:
    gl_renderer: typing.Optional[protobug.String] = protobug.field(1, default=None)
    gl_es_version_major: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    gl_es_version_minor: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


class ClientName(protobug.Enum, strict=False):
    UNKNOWN_INTERFACE = 0
    WEB = 1
    MWEB = 2
    ANDROID = 3
    IOS = 5
    TVHTML5 = 7
    TVLITE = 8
    TVANDROID = 10
    XBOX = 11
    CLIENTX = 12
    XBOXONEGUIDE = 13
    ANDROID_CREATOR = 14
    IOS_CREATOR = 15
    TVAPPLE = 16
    IOS_INSTANT = 17
    ANDROID_KIDS = 18
    IOS_KIDS = 19
    ANDROID_INSTANT = 20
    ANDROID_MUSIC = 21
    IOS_TABLOID = 22
    ANDROID_TV = 23
    ANDROID_GAMING = 24
    IOS_GAMING = 25
    IOS_MUSIC = 26
    MWEB_TIER_2 = 27
    ANDROID_VR = 28
    ANDROID_UNPLUGGED = 29
    ANDROID_TESTSUITE = 30
    WEB_MUSIC_ANALYTICS = 31
    WEB_GAMING = 32
    IOS_UNPLUGGED = 33
    ANDROID_WITNESS = 34
    IOS_WITNESS = 35
    ANDROID_SPORTS = 36
    IOS_SPORTS = 37
    ANDROID_LITE = 38
    IOS_EMBEDDED_PLAYER = 39
    IOS_DIRECTOR = 40
    WEB_UNPLUGGED = 41
    WEB_EXPERIMENTS = 42
    TVHTML5_CAST = 43
    WEB_EMBEDDED_PLAYER = 56
    TVHTML5_AUDIO = 57
    TV_UNPLUGGED_CAST = 58
    TVHTML5_KIDS = 59
    WEB_HEROES = 60
    WEB_MUSIC = 61
    WEB_CREATOR = 62
    TV_UNPLUGGED_ANDROID = 63
    IOS_LIVE_CREATION_EXTENSION = 64
    TVHTML5_UNPLUGGED = 65
    IOS_MESSAGES_EXTENSION = 66
    WEB_REMIX = 67
    IOS_UPTIME = 68
    WEB_UNPLUGGED_ONBOARDING = 69
    WEB_UNPLUGGED_OPS = 70
    WEB_UNPLUGGED_PUBLIC = 71
    TVHTML5_VR = 72
    WEB_LIVE_STREAMING = 73
    ANDROID_TV_KIDS = 74
    TVHTML5_SIMPLY = 75
    WEB_KIDS = 76
    MUSIC_INTEGRATIONS = 77
    TVHTML5_YONGLE = 80
    GOOGLE_ASSISTANT = 84
    TVHTML5_SIMPLY_EMBEDDED_PLAYER = 85
    WEB_MUSIC_EMBEDDED_PLAYER = 86
    WEB_INTERNAL_ANALYTICS = 87
    WEB_PARENT_TOOLS = 88
    GOOGLE_MEDIA_ACTIONS = 89
    WEB_PHONE_VERIFICATION = 90
    ANDROID_PRODUCER = 91
    IOS_PRODUCER = 92
    TVHTML5_FOR_KIDS = 93
    GOOGLE_LIST_RECS = 94
    MEDIA_CONNECT_FRONTEND = 95
    WEB_EFFECT_MAKER = 98
    WEB_SHOPPING_EXTENSION = 99
    WEB_PLAYABLES_PORTAL = 100
    VISIONOS = 101
    WEB_LIVE_APPS = 102
    WEB_MUSIC_INTEGRATIONS = 103
    ANDROID_MUSIC_AOSP = 104


class Theme(protobug.Enum, strict=False):
    UNKNOWN_THEME = 0
    CLASSIC = 1
    KIDS = 2
    INSTANT = 3
    CREATOR = 4
    MUSIC = 5
    GAMING = 6
    UNPLUGGED = 7
    

class ApplicationState(protobug.Enum, strict=False):
    UNKNOWN_APPLICATION_STATE = 0
    ACTIVE = 1
    BACKGROUND = 2
    INACTIVE = 3


class PlayerType(protobug.Enum, strict=False):
    UNKNOWN_PLAYER = 0
    UNPLAYABLE = 1
    UNIPLAYER = 2
    AS2 = 3
    AS3 = 4
    BLAZER_PLAYER_FULL_SCREEN = 5
    BLAZER_PLAYER_INLINE = 6
    RTSP_STREAM_LINK = 7
    HTTP_STREAM_LINK = 8
    NATIVE_APP_LINK = 9
    REMOTE = 10
    NATIVE_MEDIA_PLAYER = 11
    ANDROID_EXOPLAYER = 12
    WEB_MULTIVIEW_PLAYER = 13
    EMBEDDED_FLASH = 14
    IOS_EXOPLAYER = 15
    ANDROID_EXOPLAYER_V2 = 16
    COURTSIDE = 17
    ANDROID_EXO2_SCRIPTED_MEDIA_FETCH = 18
    PLATYPUS = 19
    ANDROID_BASE_EXOPLAYER = 20


@protobug.message
class MobileDataPlanInfo:
    cpid: typing.Optional[protobug.String] = protobug.field(49, default=None)
    serialized_data_plan_status: list[protobug.String] = protobug.field(50, default_factory=list)
    carrier_id: typing.Optional[protobug.Int64] = protobug.field(51, default=None)
    data_saving_quality_picker_enabled: typing.Optional[protobug.Bool] = protobug.field(52, default=None)
    mccmnc: typing.Optional[protobug.String] = protobug.field(53, default=None)


@protobug.message
class ConfigGroupsClientInfo:
    cold_config_data: typing.Optional[protobug.String] = protobug.field(1, default=None)
    cold_hash_data: typing.Optional[protobug.String] = protobug.field(3, default=None)
    hot_hash_data: typing.Optional[protobug.String] = protobug.field(5, default=None)
    app_install_data: typing.Optional[protobug.String] = protobug.field(6, default=None)
    active_account_static_config_data: typing.Optional[protobug.String] = protobug.field(7, default=None)
    account_static_hash_data: typing.Optional[protobug.String] = protobug.field(8, default=None)
    account_dynamic_hash_data: typing.Optional[protobug.String] = protobug.field(9, default=None)


class ConnectionType(protobug.Enum, strict=False):
    CONN_DEFAULT = 0
    CONN_UNKNOWN = 1
    CONN_NONE = 2
    CONN_WIFI = 3
    CONN_CELLULAR_2G = 4
    CONN_CELLULAR_3G = 5
    CONN_CELLULAR_4G = 6
    CONN_CELLULAR_UNKNOWN = 7
    CONN_DISCO = 8
    CONN_CELLULAR_5G = 9
    CONN_WIFI_METERED = 10
    CONN_CELLULAR_5G_SA = 11
    CONN_CELLULAR_5G_NSA = 12
    CONN_WIRED = 13
    CONN_INVALID = 14


@protobug.message
class UnpluggedLocationInfo:
    latitude_e7: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    longitude_e7: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    local_timestamp_ms: typing.Optional[protobug.Int64] = protobug.field(3, default=None)
    ip_address: typing.Optional[protobug.String] = protobug.field(4, default=None)
    timezone: typing.Optional[protobug.String] = protobug.field(5, default=None)
    prefer_24_hour_time: typing.Optional[protobug.Bool] = protobug.field(6, default=None)
    location_radius_meters: typing.Optional[protobug.Int32] = protobug.field(7, default=None)
    is_initial_load: typing.Optional[protobug.Bool] = protobug.field(8, default=None)
    browser_permission_granted: typing.Optional[protobug.Bool] = protobug.field(9, default=None)
    client_permission_state: typing.Optional[protobug.Int32] = protobug.field(10, default=None)
    location_override_token: typing.Optional[protobug.String] = protobug.field(11, default=None)


class KidsParentCurationMode(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    KIDS_PARENT_CURATION_MODE_UNKNOWN = 0
    KIDS_PARENT_CURATION_MODE_NONE = 1
    KIDS_PARENT_CURATION_MODE_CURATING = 2
    KIDS_PARENT_CURATION_MODE_PREVIEWING = 3


@protobug.message
class KidsUserEducationSettings:
    has_seen_home_chip_bar_user_education: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    has_seen_home_pivot_bar_user_education: typing.Optional[protobug.Bool] = protobug.field(2, default=None)
    has_seen_parent_muir_user_education: typing.Optional[protobug.Bool] = protobug.field(3, default=None)


@protobug.message
class KidsCategorySettings:
    enabled_categories: list[protobug.String] = protobug.field(1, default_factory=list)


@protobug.message
class KidsContentSettings:

    class KidsNoSearchMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        YT_KIDS_NO_SEARCH_MODE_UNKNOWN = 0
        YT_KIDS_NO_SEARCH_MODE_OFF = 1
        YT_KIDS_NO_SEARCH_MODE_ON = 2

    class AgeUpMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        YT_KIDS_AGE_UP_MODE_UNKNOWN = 0
        YT_KIDS_AGE_UP_MODE_OFF = 1
        YT_KIDS_AGE_UP_MODE_TWEEN = 2
        YT_KIDS_AGE_UP_MODE_PRESCHOOL = 3

    class ContentDensity(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        KIDS_CONTENT_DENSITY_UNKNOWN = 0
        KIDS_CONTENT_DENSITY_SPARSE = 1
        KIDS_CONTENT_DENSITY_DENSE = 2

    class CorpusRestriction(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        KIDS_CORPUS_RESTRICTION_UNSPECIFIED = 0
        KIDS_CORPUS_RESTRICTION_PARENT_APPROVED_ONLY = 1
        KIDS_CORPUS_RESTRICTION_HUMAN_CURATED = 2
        KIDS_CORPUS_RESTRICTION_ALGO = 3

    class CorpusPreference(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        KIDS_CORPUS_PREFERENCE_UNKNOWN = 0
        KIDS_CORPUS_PREFERENCE_YOUNGER = 1
        KIDS_CORPUS_PREFERENCE_TWEEN = 2
        KIDS_CORPUS_PREFERENCE_PAM_YOUNGER = 3
        KIDS_CORPUS_PREFERENCE_PAM_TWEEN = 4
        KIDS_CORPUS_PREFERENCE_PRESCHOOL = 5
        KIDS_CORPUS_PREFERENCE_SUPEX_MEDIUM = 6
        KIDS_CORPUS_PREFERENCE_SUPEX_LARGE = 7
        KIDS_CORPUS_PREFERENCE_SUPEX_SMALL = 8

    kids_no_search_mode: typing.Optional[KidsNoSearchMode] = protobug.field(1, default=None)
    age_up_mode: typing.Optional[AgeUpMode] = protobug.field(2, default=None)
    content_density: typing.Optional[ContentDensity] = protobug.field(3, default=None)
    corpus_restriction: typing.Optional[CorpusRestriction] = protobug.field(4, default=None)
    corpus_preference: typing.Optional[CorpusPreference] = protobug.field(6, default=None)


@protobug.message
class KidsAppInfo:
    content_settings: typing.Optional[KidsContentSettings] = protobug.field(1, default=None)
    parent_curation_mode: typing.Optional[KidsParentCurationMode] = protobug.field(2, default=None)
    category_settings: typing.Optional[KidsCategorySettings] = protobug.field(3, default=None)
    user_education_settings: typing.Optional[protobug.Bytes] = protobug.field(4, default=None)


@protobug.message
class StoreDigitalGoodsApiSupportStatus:

    class Status(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        DIGITAL_GOODS_API_SUPPORT_STATUS_UNKNOWN = 0
        DIGITAL_GOODS_API_SUPPORT_STATUS_SUPPORTED = 1
        DIGITAL_GOODS_API_SUPPORT_STATUS_UNSUPPORTED = 2

    play_store_digital_goods_api_support_status: typing.Optional[protobug.Bool] = protobug.field(1, default=None)


@protobug.message
class MusicAppInfo:

    class WebDisplayMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        WEB_DISPLAY_MODE_UNKNOWN = 0
        WEB_DISPLAY_MODE_BROWSER = 1
        WEB_DISPLAY_MODE_MINIMAL_UI = 2
        WEB_DISPLAY_MODE_STANDALONE = 3
        WEB_DISPLAY_MODE_FULLSCREEN = 4

    class MusicLocationMasterSwitch(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        MUSIC_LOCATION_MASTER_SWITCH_UNKNOWN = 0
        MUSIC_LOCATION_MASTER_SWITCH_INDETERMINATE = 1
        MUSIC_LOCATION_MASTER_SWITCH_ENABLED = 2
        MUSIC_LOCATION_MASTER_SWITCH_DISABLED = 3

    class MusicActivityMasterSwitch(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        MUSIC_ACTIVITY_MASTER_SWITCH_UNKNOWN = 0
        MUSIC_ACTIVITY_MASTER_SWITCH_INDETERMINATE = 1
        MUSIC_ACTIVITY_MASTER_SWITCH_ENABLED = 2
        MUSIC_ACTIVITY_MASTER_SWITCH_DISABLED = 3

    class PwaInstallabilityStatus(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        PWA_INSTALLABILITY_STATUS_UNKNOWN = 0
        PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED = 1

    class MusicTier(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        MUSIC_TIER_UNSPECIFIED = 0
        MUSIC_TIER_AVOD = 1
        MUSIC_TIER_MAT = 2
        MUSIC_TIER_SUBSCRIPTION = 3

    class MusicPlayBackMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        MUSIC_PLAY_BACK_MODE_UNKNOWN = 0
        MUSIC_PLAY_BACK_MODE_AUDIO = 1
        MUSIC_PLAY_BACK_MODE_VIDEO = 2

    class IosBackgroundRefreshStatus(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        IOS_BACKGROUND_REFRESH_STATUS_UNKNOWN = 0
        IOS_BACKGROUND_REFRESH_STATUS_RESTRICTED = 1
        IOS_BACKGROUND_REFRESH_STATUS_DENIED = 2
        IOS_BACKGROUND_REFRESH_STATUS_AVAILABLE = 3

    play_back_mode: typing.Optional[MusicPlayBackMode] = protobug.field(1, default=None)
    music_location_master_switch: typing.Optional[MusicLocationMasterSwitch] = protobug.field(2, default=None)
    music_activity_master_switch: typing.Optional[MusicActivityMasterSwitch] = protobug.field(3, default=None)
    offline_mixtape_enabled: typing.Optional[protobug.Bool] = protobug.field(4, default=None)
    auto_offline_enabled: typing.Optional[protobug.Bool] = protobug.field(5, default=None)
    ios_background_refresh_status: typing.Optional[IosBackgroundRefreshStatus] = protobug.field(6, default=None)
    smart_downloads_song_limit: typing.Optional[protobug.Int32] = protobug.field(7, default=None)
    transitioned_from_mixtape_to_smart_downloads: typing.Optional[protobug.Bool] = protobug.field(8, default=None)
    pwa_installability_status: typing.Optional[PwaInstallabilityStatus] = protobug.field(9, default=None)
    web_display_mode: typing.Optional[WebDisplayMode] = protobug.field(10, default=None)
    music_tier: typing.Optional[MusicTier] = protobug.field(11, default=None)
    store_digital_goods_api_support_status: typing.Optional[StoreDigitalGoodsApiSupportStatus] = protobug.field(12, default=None)
    smart_downloads_time_since_last_opt_out_sec: typing.Optional[protobug.Int64] = protobug.field(13, default=None)
    multi_player_entities_enabled: typing.Optional[protobug.Bool] = protobug.field(14, default=None)


@protobug.message
class VoiceCapability:
    has_soft_mic_support: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    has_hard_mic_support: typing.Optional[protobug.Bool] = protobug.field(2, default=None)


@protobug.message
class TvAppInfo:

    class TvAppQuality(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        TV_APP_QUALITY_UNKNOWN = 0
        TV_APP_QUALITY_LIMITED_MEMORY = 1
        TV_APP_QUALITY_LIMITED_ANIMATION = 2
        TV_APP_QUALITY_FULL_ANIMATION = 3

    class LivingRoomAppMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        LIVING_ROOM_APP_MODE_UNSPECIFIED = 0
        LIVING_ROOM_APP_MODE_MAIN = 1
        LIVING_ROOM_APP_MODE_KIDS = 2
        LIVING_ROOM_APP_MODE_MUSIC = 3
        LIVING_ROOM_APP_MODE_UNPLUGGED = 4
        LIVING_ROOM_APP_MODE_GAMING = 5

    class CobaltReleaseVehicle(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        COBALT_RELEASE_VEHICLE_UNKNOWN = 0
        COBALT_RELEASE_VEHICLE_EVERGREEN = 1
        COBALT_RELEASE_VEHICLE_EVERGREEN_LITE = 2
        COBALT_RELEASE_VEHICLE_PLAYSTATION_3 = 3
        COBALT_RELEASE_VEHICLE_PLAYSTATION_4 = 4
        COBALT_RELEASE_VEHICLE_PLAYSTATION_4_UNPLUGGED = 5
        COBALT_RELEASE_VEHICLE_PLAYSTATION_4_KIDS = 6
        COBALT_RELEASE_VEHICLE_PLAYSTATION_5 = 7
        COBALT_RELEASE_VEHICLE_PLAYSTATION_5_KIDS = 8
        COBALT_RELEASE_VEHICLE_PLAYSTATION_5_UNPLUGGED = 9
        COBALT_RELEASE_VEHICLE_APPLE_TV = 10
        COBALT_RELEASE_VEHICLE_APPLE_TV_UNPLUGGED = 11
        COBALT_RELEASE_VEHICLE_APPLE_TV_KIDS = 12
        COBALT_RELEASE_VEHICLE_ANDROID_TV = 13
        COBALT_RELEASE_VEHICLE_ANDROID_TV_UNPLUGGED = 14
        COBALT_RELEASE_VEHICLE_ANDROID_TV_KIDS = 15
        COBALT_RELEASE_VEHICLE_SWITCH = 16
        COBALT_RELEASE_VEHICLE_XBOX = 17
        COBALT_RELEASE_VEHICLE_XBOX_UNPLUGGED = 18
        COBALT_RELEASE_VEHICLE_XBOX_KIDS = 19
        COBALT_RELEASE_VEHICLE_LEGACY_THIRD_PARTY = 20

    class AndroidOSExperience(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        ANDROID_OS_EXPERIENCE_UNKNOWN = 0
        ANDROID_OS_EXPERIENCE_AMATI = 1
        ANDROID_OS_EXPERIENCE_WATSON = 2

    class InAppBackgroundingMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        IN_APP_BACKGROUNDING_MODE_UNKNOWN = 0
        IN_APP_BACKGROUNDING_MODE_UNSUPPORTED = 1
        IN_APP_BACKGROUNDING_MODE_FULL_CORPUS = 2
        IN_APP_BACKGROUNDING_MODE_MUSIC_CORPUS = 3

    is_first_launch: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    app_quality: typing.Optional[TvAppQuality] = protobug.field(2, default=None)
    mdx_impacted_sessions_server_events: typing.Optional[protobug.String] = protobug.field(3, default=None)
    living_room_app_mode: typing.Optional[LivingRoomAppMode] = protobug.field(4, default=None)
    device_year: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    enable_privacy_filter: typing.Optional[protobug.Bool] = protobug.field(6, default=None)
    zylon_left_nav: typing.Optional[protobug.Bool] = protobug.field(7, default=None)
    certification_scope: typing.Optional[protobug.String] = protobug.field(9, default=None)
    living_room_po_token_id: typing.Optional[protobug.String] = protobug.field(10, default=None)
    js_engine_string: typing.Optional[protobug.String] = protobug.field(12, default=None)
    voice_capability: typing.Optional[VoiceCapability] = protobug.field(13, default=None)
    system_integrator: typing.Optional[protobug.String] = protobug.field(14, default=None)
    recent_voice_usage_count: typing.Optional[protobug.Int32] = protobug.field(15, default=None)
    release_vehicle: typing.Optional[CobaltReleaseVehicle] = protobug.field(16, default=None)
    android_os_experience: typing.Optional[AndroidOSExperience] = protobug.field(17, default=None)
    android_build_fingerprint: typing.Optional[protobug.String] = protobug.field(18, default=None)
    cobalt_app_version: typing.Optional[protobug.String] = protobug.field(19, default=None)
    cobalt_starboard_version: typing.Optional[protobug.String] = protobug.field(20, default=None)
    in_app_backgrounding_mode: typing.Optional[InAppBackgroundingMode] = protobug.field(21, default=None)
    use_start_playback_preview_command: typing.Optional[protobug.Bool] = protobug.field(22, default=None)
    should_show_persistent_signin_on_home: typing.Optional[protobug.Bool] = protobug.field(23, default=None)
    android_play_services_version: typing.Optional[protobug.String] = protobug.field(24, default=None)
    supports_native_scrolling: typing.Optional[protobug.Bool] = protobug.field(25, default=None)


@protobug.message
class UnpluggedAppInfo:
    class VoiceRemoteState(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        VOICE_REMOTE_STATE_UNKNOWN = 0
        VOICE_REMOTE_STATE_ENABLED = 1
        VOICE_REMOTE_STATE_DISABLED = 2

    class MicrophonePermissionState(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        MICROPHONE_PERMISSION_STATE_UNKNOWN = 0
        MICROPHONE_PERMISSION_STATE_ALLOWED = 1
        MICROPHONE_PERMISSION_STATE_DENIED = 2
        MICROPHONE_PERMISSION_STATE_HARD_DENIED = 3

    class UnpluggedMultiSizeType(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        UNPLUGGED_MULTI_SIZE_TYPE_UNKNOWN = 0
        UNPLUGGED_MULTI_SIZE_TYPE_COMPACT = 1
        UNPLUGGED_MULTI_SIZE_TYPE_REGULAR = 2

    class UnpluggedFilterModeType(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        UNPLUGGED_FILTER_MODE_TYPE_UNKNOWN = 0
        UNPLUGGED_FILTER_MODE_TYPE_NONE = 1
        UNPLUGGED_FILTER_MODE_TYPE_PG = 2
        UNPLUGGED_FILTER_MODE_TYPE_PG_THIRTEEN = 3

    enable_safety_mode: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    enable_filter_mode: typing.Optional[protobug.Bool] = protobug.field(2, default=None)
    ios_notification_permission: typing.Optional[protobug.Bool] = protobug.field(3, default=None)
    microphone_permission_state: typing.Optional[MicrophonePermissionState] = protobug.field(4, default=None)
    voice_remote_state: typing.Optional[VoiceRemoteState] = protobug.field(5, default=None)
    multi_size_type: typing.Optional[UnpluggedMultiSizeType] = protobug.field(6, default=None)
    force_enable_epg_3: typing.Optional[protobug.Bool] = protobug.field(7, default=None)
    filter_mode_type: typing.Optional[UnpluggedFilterModeType] = protobug.field(8, default=None)


@protobug.message
class UlrStatus:
    reporting_enabled_setting: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    history_enabled_setting: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    is_allowed: typing.Optional[protobug.Bool] = protobug.field(3, default=None)
    is_active: typing.Optional[protobug.Bool] = protobug.field(4, default=None)
    expected_opt_in_result: typing.Optional[protobug.Int32] = protobug.field(5, default=None)


@protobug.message
class LocationInfo:
    class LocationInfoStatus(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        LOCATION_INFO_STATUS_UNKNOWN = 0
        LOCATION_INFO_STATUS_NOT_READY = 1
        LOCATION_INFO_STATUS_OK_ALWAYS = 2
        LOCATION_INFO_STATUS_OK_APP_IN_USE = 3
        LOCATION_INFO_STATUS_PERMS_NOT_YET_GRANTED = 4
        LOCATION_INFO_STATUS_PERMS_REJECTED = 5
        LOCATION_INFO_STATUS_PRECISE_LOCATION_NOT_SUPPORTED = 6
        LOCATION_INFO_STATUS_LOCATION_SERVICES_DISABLED = 7
        LOCATION_INFO_STATUS_ERROR = 8

    class LocationPermissionAuthorizationStatus(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_UNKNOWN = 0
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_UNSUPPORTED = 1
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_DISABLED = 2
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_NOT_YET_GRANTED = 3
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_REJECTED = 4
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_ALWAYS = 5
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_APP_IN_USE = 6
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_NOT_YET_GRANTED_WAS_APP_IN_USE = 7
        LOCATION_PERMISSION_AUTHORIZATION_STATUS_ALWAYS_PROVISIONAL = 8

    location_info_status: typing.Optional[LocationInfoStatus] = protobug.field(1, default=None)
    ulr_status: typing.Optional[UlrStatus] = protobug.field(2, default=None)
    latitude_e7: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    longitude_e7: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    horizontal_accuracy_meters: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    location_freshness_ms: typing.Optional[protobug.Int64] = protobug.field(6, default=None)
    location_permission_authorization_status: typing.Optional[LocationPermissionAuthorizationStatus] = protobug.field(7, default=None)
    location_override_token: typing.Optional[protobug.String] = protobug.field(8, default=None)
    force_location_playability_token_refresh: typing.Optional[protobug.Bool] = protobug.field(9, default=None)


class UserInterfaceTheme(protobug.Enum, strict=False):
    USER_INTERFACE_THEME_UNKNOWN = 0
    USER_INTERFACE_THEME_LIGHT = 1
    USER_INTERFACE_THEME_DARK = 2


@protobug.message
class HeterodyneExperimentIds:
    clear_blob: typing.Optional[protobug.Bytes] = protobug.field(1, default=None)
    encrypted_blob: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)
    users_match: typing.Optional[protobug.Bool] = protobug.field(3, default=None)
    clear_blob_js: typing.Optional[protobug.String] = protobug.field(4, default=None)


@protobug.message
class NotificationPermissionInfo:

    class NotificationSetting(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        NOTIFICATIONS_SETTING_UNKNOWN = 0
        NOTIFICATIONS_SETTING_ENABLED = 1
        NOTIFICATIONS_SETTING_DISABLED_OS_LEVEL = 2
        NOTIFICATIONS_SETTING_DISABLED_APP_LEVEL = 3
        NOTIFICATIONS_SETTING_DISABLED_SUBS_NOTIFICATION_CHANNEL_LEVEL = 4
        NOTIFICATIONS_SETTING_IOS_UNPROMPTED = 5

    notification_setting: typing.Optional[NotificationSetting] = protobug.field(1, default=None)
    last_device_opt_in_change_time_ago_sec: typing.Optional[protobug.Int64] = protobug.field(2, default=None)


@protobug.message
class ClientStoreInfo:
    ios_store_country_code: typing.Optional[protobug.String] = protobug.field(1, default=None)


@protobug.message
class DataPushBuild:

    class AccessType(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        ACCESS_TYPE_UNKNOWN = 0
        ACCESS_TYPE_EMBEDDED = 1
        ACCESS_TYPE_COLD = 2
        ACCESS_TYPE_HOT = 3

    build_id: typing.Optional[protobug.Int64] = protobug.field(1, default=None)
    client_experiment_id: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    access_type: typing.Optional[AccessType] = protobug.field(3, default=None)


@protobug.message
class SRSDataPushVersion:
    datapush_build: typing.Optional[DataPushBuild] = protobug.field(1, default=None)


@protobug.message
class PlayerDataPushVersion:
    datapush_build: typing.Optional[DataPushBuild] = protobug.field(1, default=None)


class ClientScreen(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    UNKNOWN = 0
    WATCH = 1
    CHANNEL = 2
    EMBED = 3
    KIDS_SING_ALONG = 4
    LIVE_MONITOR = 5
    WATCH_FULL_SCREEN = 6
    UPLOAD_EXTENSION = 7
    ADUNIT = 8
    REELS = 9


class MwebUi(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    UNKNOWN_MWEB_UI = 0
    V2 = 1
    BLAZER = 2


class HardwarePlatform(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    UNKNOWN_PLATFORM = 0
    DESKTOP = 1
    TV = 2
    GAME_CONSOLE = 3
    MOBILE = 4
    TABLET = 5


@protobug.message
class ConnectedClientInfo:
    package_name: typing.Optional[protobug.String] = protobug.field(1, default=None)
    last_connected_at: typing.Optional[protobug.Int64] = protobug.field(2, default=None)
    is_request_initiator: typing.Optional[protobug.Bool] = protobug.field(3, default=None)


@protobug.message
class HomeGroupInfoHomeDevice:
    class Capability(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        HOME_DEVICE_CAPABILITY_UNKNOWN = 0
        HOME_DEVICE_CAPABILITY_DISPLAY_SUPPORTED = 1

    capabilities: list[Capability] = protobug.field(1, default_factory=list)


@protobug.message
class HomeGroupInfo:
    is_part_of_group: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    devices: list[HomeGroupInfoHomeDevice] = protobug.field(2, default_factory=list)
    is_group_owner: typing.Optional[protobug.Bool] = protobug.field(3, default=None)


@protobug.message
class SpacecastClientInfoSpacecastAppliance:

    class Status(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        FAKE = 0
        UNKNOWN = 1
        HEALTHY = 2
        UNHEALTHY = 3
        UNREACHABLE_TIMEOUT = 4
        UNREACHABLE_NETWORK_ERROR = 5
        OVERLOADED = 6

    # todo: get mapping
    # hostname: typing.Optional[protobug.String] = protobug.field(??, default=None)
    # device_id: typing.Optional[protobug.String] = protobug.field(??, default=None)
    # active: typing.Optional[protobug.Bool] = protobug.field(??, default=None)
    # status: typing.Optional[protobug.String] = protobug.field(??, default=None)
    # content_profile_token: typing.Optional[protobug.String] = protobug.field(??, default=None)


@protobug.message
class SpacecastClientInfo:

    class InteractionLevel(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        SPACECAST_INTERACTION_LEVEL_UNKNOWN = 0
        SPACECAST_INTERACTION_LEVEL_DISCOVERY_ONLY = 1
        SPACECAST_INTERACTION_LEVEL_PLAYBACK = 2

    appliances: list[SpacecastClientInfoSpacecastAppliance] = protobug.field(1, default_factory=list)
    interaction_level: typing.Optional[InteractionLevel] = protobug.field(2, default=None)


class PlatformDetail(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    PLATFORM_DETAIL_UNKNOWN = 0
    PLATFORM_DETAIL_TV = 1
    PLATFORM_DETAIL_STB = 2
    PLATFORM_DETAIL_BDP = 3
    PLATFORM_DETAIL_OTT = 4
    PLATFORM_DETAIL_GAME = 5
    PLATFORM_DETAIL_ATV = 6


class EffectiveConnectionType(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    EFFECTIVE_CONNECTION_TYPE_UNKNOWN = 0
    EFFECTIVE_CONNECTION_TYPE_OFFLINE = 1
    EFFECTIVE_CONNECTION_TYPE_SLOW_2G = 2
    EFFECTIVE_CONNECTION_TYPE_2G = 3
    EFFECTIVE_CONNECTION_TYPE_3G = 4
    EFFECTIVE_CONNECTION_TYPE_4G = 5


@protobug.message
class MainAppWebInfo:

    class PwaInstallabilityStatus(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        PWA_INSTALLABILITY_STATUS_UNKNOWN = 0
        PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED = 1

    class WebDisplayMode(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        WEB_DISPLAY_MODE_UNKNOWN = 0
        WEB_DISPLAY_MODE_BROWSER = 1
        WEB_DISPLAY_MODE_MINIMAL_UI = 2
        WEB_DISPLAY_MODE_STANDALONE = 3
        WEB_DISPLAY_MODE_FULLSCREEN = 4

    graft_url: typing.Optional[protobug.String] = protobug.field(1, default=None)
    pwa_installability_status: typing.Optional[PwaInstallabilityStatus] = protobug.field(2, default=None)
    web_display_mode: typing.Optional[WebDisplayMode] = protobug.field(3, default=None)
    is_web_native_share_available: typing.Optional[protobug.Bool] = protobug.field(4, default=None)
    store_digital_goods_api_support_status: typing.Optional[StoreDigitalGoodsApiSupportStatus] = protobug.field(5, default=None)


@protobug.message
class ClientInfo:
    hl: typing.Optional[protobug.String] = protobug.field(1, default=None)
    gl: typing.Optional[protobug.String] = protobug.field(2, default=None)
    remote_host: typing.Optional[protobug.String] = protobug.field(4, default=None)

    device_id: typing.Optional[protobug.String] = protobug.field(6, default=None)

    debug_device_id_override: typing.Optional[protobug.String] = protobug.field(8, default=None)
    experiment_ids: list[protobug.Int32] = protobug.field(9, default_factory=list)
    carrier_geo: typing.Optional[protobug.String] = protobug.field(10, default=None)
    cracked_hl: typing.Optional[protobug.Bool] = protobug.field(11, default=None)
    device_make: typing.Optional[protobug.String] = protobug.field(12, default=None)
    device_model: typing.Optional[protobug.String] = protobug.field(13, default=None)
    visitor_data: typing.Optional[protobug.String] = protobug.field(14, default=None)
    user_agent: typing.Optional[protobug.String] = protobug.field(15, default=None)
    client_name: typing.Optional[ClientName] = protobug.field(16, default=None)
    client_version: typing.Optional[protobug.String] = protobug.field(17, default=None)
    os_name: typing.Optional[protobug.String] = protobug.field(18, default=None)
    os_version: typing.Optional[protobug.String] = protobug.field(19, default=None)
    project_id: typing.Optional[protobug.String] = protobug.field(20, default=None)
    accept_language: typing.Optional[protobug.String] = protobug.field(21, default=None)
    accept_region: typing.Optional[protobug.String] = protobug.field(22, default=None)
    original_url: typing.Optional[protobug.String] = protobug.field(23, default=None)

    raw_device_id: typing.Optional[protobug.String] = protobug.field(25, default=None)

    config_data: typing.Optional[protobug.String] = protobug.field(27, default=None)
    client_screen: typing.Optional[ClientScreen] = protobug.field(28, default=None)
    mweb_ui: typing.Optional[MwebUi] = protobug.field(29, default=None)
    theme: typing.Optional[Theme] = protobug.field(30, default=None)
    spacecast_token: typing.Optional[protobug.String] = protobug.field(31, default=None)

    application_state: typing.Optional[ApplicationState] = protobug.field(35, default=None)
    player_type: typing.Optional[PlayerType] = protobug.field(36, default=None)
    screen_width_points: typing.Optional[protobug.Int32] = protobug.field(37, default=None)
    screen_height_points: typing.Optional[protobug.Int32] = protobug.field(38, default=None)
    screen_width_inches: typing.Optional[protobug.Float] = protobug.field(39, default=None)
    screen_height_inches: typing.Optional[protobug.Float] = protobug.field(40, default=None)
    screen_pixel_density: typing.Optional[protobug.Int32] = protobug.field(41, default=None)
    platform: typing.Optional[HardwarePlatform] = protobug.field(42, default=None)

    spacecast_client_info: typing.Optional[SpacecastClientInfo] = protobug.field(45, default=None)
    client_form_factor: typing.Optional[ClientFormFactor] = protobug.field(46, default=None)

    forwarded_for: typing.Optional[protobug.String] = protobug.field(48, default=None)
    mobile_data_plan_info: typing.Optional[MobileDataPlanInfo] = protobug.field(49, default=None)
    gmscore_version_code: typing.Optional[protobug.Int32] = protobug.field(50, default=None)
    webp_support: typing.Optional[protobug.Bool] = protobug.field(51, default=None)

    experiments_token: typing.Optional[protobug.String] = protobug.field(54, default=None)
    window_width_points: typing.Optional[protobug.Int32] = protobug.field(55, default=None)
    window_height_points: typing.Optional[protobug.Int32] = protobug.field(56, default=None)

    connection_type: typing.Optional[ConnectionType] = protobug.field(61, default=None)  # seen on android = 6
    config_info: typing.Optional[ConfigGroupsClientInfo] = protobug.field(62, default=None)
    unplugged_location_info: typing.Optional[UnpluggedLocationInfo] = protobug.field(63, default=None)
    android_sdk_version: typing.Optional[protobug.Int32] = protobug.field(64, default=None)
    screen_density_float: typing.Optional[protobug.Float] = protobug.field(65, default=None)
    first_time_sign_in_experiment_ids: list[protobug.Int32] = protobug.field(66, default_factory=list)
    utc_offset_minutes: typing.Optional[protobug.Int32] = protobug.field(67, default=None)
    animated_webp_support: typing.Optional[protobug.Bool] = protobug.field(68, default=None)
    kids_app_info: typing.Optional[KidsAppInfo] = protobug.field(69, default=None)
    music_app_info: typing.Optional[MusicAppInfo] = protobug.field(70, default=None)
    tv_app_info: typing.Optional[TvAppInfo] = protobug.field(71, default=None)
    internal_geo_ip: typing.Optional[protobug.String] = protobug.field(72, default=None)
    unplugged_app_info: typing.Optional[UnpluggedAppInfo] = protobug.field(73, default=None)
    location_info: typing.Optional[LocationInfo] = protobug.field(74, default=None)

    content_size_category: typing.Optional[protobug.String] = protobug.field(76, default=None)
    font_scale: typing.Optional[protobug.Float] = protobug.field(77, default=None)
    user_interface_theme: typing.Optional[UserInterfaceTheme] = protobug.field(78, default=None)

    time_zone: typing.Optional[protobug.String] = protobug.field(80, default=None)
    home_group_info: typing.Optional[HomeGroupInfo] = protobug.field(81, default=None)

    eml_template_context: typing.Optional[protobug.Bytes] = protobug.field(84, default=None)
    cold_app_bundle_config_data: typing.Optional[protobug.Bytes] = protobug.field(85, default=None)
    heterodyne_ids: list[HeterodyneExperimentIds] = protobug.field(86, default_factory=list)
    browser_name: typing.Optional[protobug.String] = protobug.field(87, default=None)
    browser_version: typing.Optional[protobug.String] = protobug.field(88, default=None)
    location_playability_token: typing.Optional[protobug.String] = protobug.field(89, default=None)
    platform_details: typing.Optional[PlatformDetail] = protobug.field(90, default=None)
    release_year: typing.Optional[protobug.Int32] = protobug.field(91, default=None)
    chipset: typing.Optional[protobug.String] = protobug.field(92, default=None)
    firmware_version: typing.Optional[protobug.String] = protobug.field(93, default=None)
    effective_connection_type: typing.Optional[EffectiveConnectionType] = protobug.field(94, default=None)
    memory_total_kbytes: typing.Optional[protobug.Int64] = protobug.field(95, default=None)
    main_app_web_info: typing.Optional[MainAppWebInfo] = protobug.field(96, default=None)
    notification_permission_info: typing.Optional[NotificationPermissionInfo] = protobug.field(97, default=None)
    device_brand: typing.Optional[protobug.String] = protobug.field(98, default=None)  # seen on android = "google"
    client_store_info: typing.Optional[ClientStoreInfo] = protobug.field(99, default=None)
    srs_datapush_build_ids: typing.Optional[SRSDataPushVersion] = protobug.field(100, default=None)
    player_datapush_build_ids: typing.Optional[PlayerDataPushVersion] = protobug.field(101, default=None)
    gl_device_info: typing.Optional[GLDeviceInfo] = protobug.field(102, default=None)
    accept_header: typing.Optional[protobug.String] = protobug.field(103, default=None)
    device_experiment_id: typing.Optional[protobug.String] = protobug.field(104, default=None)
    encoded_hacks: typing.Optional[protobug.Int64] = protobug.field(105, default=None)
    is_supervised_device: typing.Optional[protobug.Bool] = protobug.field(107, default=None)
    rollout_token: typing.Optional[protobug.String] = protobug.field(108, default=None)
    connected_client_info: typing.Optional[ConnectedClientInfo] = protobug.field(109, default=None)
