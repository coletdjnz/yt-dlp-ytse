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
    # mccmnc: typing.Optional[protobug.String] = protobug.field(??, default=None)


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
class ClientInfo:
    hl: typing.Optional[protobug.String] = protobug.field(1, default=None)
    gl: typing.Optional[protobug.String] = protobug.field(2, default=None)
    geo: typing.Optional[protobug.String] = protobug.field(3, default=None)
    remote_host: typing.Optional[protobug.String] = protobug.field(4, default=None)

    device_id: typing.Optional[protobug.String] = protobug.field(6, default=None)
    is_internal: typing.Optional[protobug.Bool] = protobug.field(7, default=None)
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
    internal_experiment_ids: list[protobug.Int32] = protobug.field(24, default_factory=list)
    raw_device_id: typing.Optional[protobug.String] = protobug.field(25, default=None)
    client_valid: typing.Optional[protobug.Bool] = protobug.field(26, default=None)
    config_data: typing.Optional[protobug.String] = protobug.field(27, default=None)

    theme: typing.Optional[Theme] = protobug.field(30, default=None)
    spacecast_token: typing.Optional[protobug.String] = protobug.field(31, default=None)
    internal_client_experiment_ids: list[protobug.Int32] = protobug.field(32, default_factory=list)
    internal_geo: typing.Optional[protobug.String] = protobug.field(34, default=None)
    application_state: typing.Optional[ApplicationState] = protobug.field(35, default=None)
    player_type: typing.Optional[PlayerType] = protobug.field(36, default=None)
    screen_width_points: typing.Optional[protobug.Int32] = protobug.field(37, default=None)
    screen_height_points: typing.Optional[protobug.Int32] = protobug.field(38, default=None)
    screen_width_inches: typing.Optional[protobug.Float] = protobug.field(39, default=None)
    screen_height_inches: typing.Optional[protobug.Float] = protobug.field(40, default=None)
    screen_pixel_density: typing.Optional[protobug.Int32] = protobug.field(41, default=None)
    
    gfe_frontline_info: typing.Optional[protobug.String] = protobug.field(43, default=None)
    yt_safety_mode_header: typing.Optional[protobug.String] = protobug.field(44, default=None)

    client_form_factor: typing.Optional[ClientFormFactor] = protobug.field(46, default=None)

    forwarded_for: typing.Optional[protobug.String] = protobug.field(48, default=None)
    mobile_data_plan_info: typing.Optional[MobileDataPlanInfo] = protobug.field(49, default=None)
    gmscore_version_code: typing.Optional[protobug.Int32] = protobug.field(50, default=None)
    webp_support: typing.Optional[protobug.Bool] = protobug.field(51, default=None)

    yt_restrict_header: typing.Optional[protobug.String] = protobug.field(53, default=None)
    experiments_token: typing.Optional[protobug.String] = protobug.field(54, default=None)
    window_width_points: typing.Optional[protobug.Int32] = protobug.field(55, default=None)
    window_height_points: typing.Optional[protobug.Int32] = protobug.field(56, default=None)

    connection_type: typing.Optional[ConnectionType] = protobug.field(61, default=None)  # seen on android = 6
    config_info: typing.Optional[ConfigGroupsClientInfo] = protobug.field(62, default=None)
    unplugged_location_info: typing.Optional[UnpluggedLocationInfo] = protobug.field(63, default=None)
    android_sdk_version: typing.Optional[protobug.Int32] = protobug.field(64, default=None)
    screen_density_float: typing.Optional[protobug.Float] = protobug.field(65, default=None)
    first_time_sign_in_experiment_ids: list[protobug.Int32] = protobug.field(66, default_factory=list)
    utc_offset_minutes: typing.Optional[protobug.Int64] = protobug.field(67, default=None)
    animated_webp_support: typing.Optional[protobug.Bool] = protobug.field(68, default=None)
    kids_app_info: typing.Optional[KidsAppInfo] = protobug.field(69, default=None)
    music_app_info: typing.Optional[MusicAppInfo] = protobug.field(70, default=None)
    tv_app_info: typing.Optional[protobug.Bytes] = protobug.field(71, default=None)  # todo: proto

    internal_geo_ip: typing.Optional[protobug.String] = protobug.field(72, default=None)
    unplugged_app_info: typing.Optional[protobug.Bytes] = protobug.field(73, default=None)  # todo: proto
    location_info: typing.Optional[protobug.Bytes] = protobug.field(74, default=None)  # todo: proto

    content_size_category: typing.Optional[protobug.String] = protobug.field(76, default=None)
    font_scale: typing.Optional[protobug.Float] = protobug.field(77, default=None)
    user_interface_theme: typing.Optional[protobug.Bytes] = protobug.field(78, default=None)  # todo: proto
    new_visitor_cookie: typing.Optional[protobug.Bool] = protobug.field(79, default=None)
    time_zone: typing.Optional[protobug.String] = protobug.field(80, default=None)

    eml_template_context: typing.Optional[protobug.Bytes] = protobug.field(84, default=None)
    cold_app_bundle_config_data: typing.Optional[protobug.Bytes] = protobug.field(85, default=None)
    heterodyne_ids: list[protobug.Bytes] = protobug.field(86, default_factory=list)  # todo: proto
    browser_name: typing.Optional[protobug.String] = protobug.field(87, default=None)
    browser_version: typing.Optional[protobug.String] = protobug.field(88, default=None)
    location_playability_token: typing.Optional[protobug.String] = protobug.field(89, default=None)

    release_year: typing.Optional[protobug.Int32] = protobug.field(91, default=None)
    chipset: typing.Optional[protobug.String] = protobug.field(92, default=None)
    firmware_version: typing.Optional[protobug.String] = protobug.field(93, default=None)

    memory_total_kbytes: typing.Optional[protobug.Int64] = protobug.field(95, default=None)

    notification_permission_info: typing.Optional[protobug.Bytes] = protobug.field(97, default=None)  # todo: proto
    device_brand: typing.Optional[protobug.String] = protobug.field(98, default=None)  # seen on android = "google"
    client_store_info: typing.Optional[protobug.Bytes] = protobug.field(99, default=None)  # todo: proto
    srs_datapush_build_ids: typing.Optional[protobug.Bytes] = protobug.field(100, default=None)  # todo: proto
    player_datapush_build_ids: typing.Optional[protobug.Bytes] = protobug.field(101, default=None)  # todo: proto
    gl_device_info: typing.Optional[GLDeviceInfo] = protobug.field(102, default=None)
    accept_header: typing.Optional[protobug.String] = protobug.field(103, default=None)
    device_experiment_id: typing.Optional[protobug.String] = protobug.field(104, default=None)
