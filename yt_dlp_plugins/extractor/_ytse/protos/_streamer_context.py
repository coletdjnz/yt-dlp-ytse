import typing
import protobug


class ClientFormFactor(protobug.Enum, strict=False):
    UNKNOWN_FORM_FACTOR = 0
    FORM_FACTOR_VAL1 = 1
    FORM_FACTOR_VAL2 = 2


@protobug.message
class GLDeviceInfo:
    gl_renderer: typing.Optional[protobug.String] = protobug.field(1, default=None)
    gl_es_version_major: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    gl_es_version_minor: typing.Optional[protobug.Int32] = protobug.field(3, default=None)


@protobug.message
class ClientInfo:
    device_make: typing.Optional[protobug.String] = protobug.field(12, default=None)
    device_model: typing.Optional[protobug.String] = protobug.field(13, default=None)
    client_name: typing.Optional[protobug.Int32] = protobug.field(16, default=None)
    client_version: typing.Optional[protobug.String] = protobug.field(17, default=None)
    os_name: typing.Optional[protobug.String] = protobug.field(18, default=None)
    os_version: typing.Optional[protobug.String] = protobug.field(19, default=None)
    accept_language: typing.Optional[protobug.String] = protobug.field(21, default=None)
    accept_region: typing.Optional[protobug.String] = protobug.field(22, default=None)
    screen_width_points: typing.Optional[protobug.Int32] = protobug.field(37, default=None)
    screen_height_points: typing.Optional[protobug.Int32] = protobug.field(38, default=None)
    screen_width_inches: typing.Optional[protobug.Float] = protobug.field(39, default=None)
    screen_height_inches: typing.Optional[protobug.Float] = protobug.field(40, default=None)
    screen_pixel_density: typing.Optional[protobug.Int32] = protobug.field(41, default=None)
    client_form_factor: typing.Optional[ClientFormFactor] = protobug.field(46, default=None)
    gmscore_version_code: typing.Optional[protobug.Int32] = protobug.field(50, default=None)
    window_width_points: typing.Optional[protobug.Int32] = protobug.field(55, default=None)
    window_height_points: typing.Optional[protobug.Int32] = protobug.field(56, default=None)
    unknwon_field_61: typing.Optional[protobug.Int32] = protobug.field(61, default=None)  # seen on android = 6
    android_sdk_version: typing.Optional[protobug.Int32] = protobug.field(64, default=None)
    screen_density_float: typing.Optional[protobug.Float] = protobug.field(65, default=None)
    utc_offset_minutes: typing.Optional[protobug.Int64] = protobug.field(67, default=None)
    time_zone: typing.Optional[protobug.String] = protobug.field(80, default=None)
    chipset: typing.Optional[protobug.String] = protobug.field(92, default=None)
    unknown_field_98: typing.Optional[protobug.String] = protobug.field(98, default=None)  # seen on android = "google"
    gl_device_info: typing.Optional[GLDeviceInfo] = protobug.field(102, default=None)

@protobug.message
class Fqa:
    type: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    value: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)


@protobug.message
class Hqa:
    code: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    message: typing.Optional[protobug.String] = protobug.field(2, default=None)


@protobug.message
class Gqa:
    field1: typing.Optional[protobug.Bytes] = protobug.field(1, default=None)
    field2: typing.Optional[Hqa] = protobug.field(2, default=None)


@protobug.message
class StreamerContext:
    client_info: ClientInfo = protobug.field(1, default=None)
    po_token: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)
    playback_cookie: typing.Optional[protobug.Bytes] = protobug.field(3, default=None)
    gp: typing.Optional[protobug.Bytes] = protobug.field(4, default=None)
    field5: list[Fqa] = protobug.field(5, default_factory=list)
    field6: list[protobug.Int32] = protobug.field(6, default_factory=list)
    field7: typing.Optional[protobug.String] = protobug.field(7, default=None)
    field8: typing.Optional[Gqa] = protobug.field(8, default=None)
