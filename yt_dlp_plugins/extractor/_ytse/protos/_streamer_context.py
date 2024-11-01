import typing
import protobug
import enum

class ClientFormFactor(enum.IntEnum):
    UNKNOWN_FORM_FACTOR = 0
    FORM_FACTOR_VAL1 = 1
    FORM_FACTOR_VAL2 = 2


@protobug.message
class GLDeviceInfo:
    gl_renderer: typing.Optional[protobug.String] = protobug.field(1)
    gl_es_version_major: typing.Optional[protobug.Int32] = protobug.field(2)
    gl_es_version_minor: typing.Optional[protobug.Int32] = protobug.field(3)


@protobug.message
class ClientInfo:
    device_make: typing.Optional[protobug.String] = protobug.field(12)
    device_model: typing.Optional[protobug.String] = protobug.field(13)
    client_name: typing.Optional[protobug.Int32] = protobug.field(16)
    client_version: typing.Optional[protobug.String] = protobug.field(17)
    os_name: typing.Optional[protobug.String] = protobug.field(18)
    os_version: typing.Optional[protobug.String] = protobug.field(19)
    accept_language: typing.Optional[protobug.String] = protobug.field(21)
    accept_region: typing.Optional[protobug.String] = protobug.field(22)
    screen_width_points: typing.Optional[protobug.Int32] = protobug.field(37)
    screen_height_points: typing.Optional[protobug.Int32] = protobug.field(38)
    screen_width_inches: typing.Optional[protobug.Float] = protobug.field(39)
    screen_height_inches: typing.Optional[protobug.Float] = protobug.field(40)
    screen_pixel_density: typing.Optional[protobug.Int32] = protobug.field(41)
    client_form_factor: typing.Optional[ClientFormFactor] = protobug.field(46)
    gmscore_version_code: typing.Optional[protobug.Int32] = protobug.field(50)
    window_width_points: typing.Optional[protobug.Int32] = protobug.field(55)
    window_height_points: typing.Optional[protobug.Int32] = protobug.field(56)
    android_sdk_version: typing.Optional[protobug.Int32] = protobug.field(64)
    screen_density_float: typing.Optional[protobug.Float] = protobug.field(65)
    utc_offset_minutes: typing.Optional[protobug.Int64] = protobug.field(67)
    time_zone: typing.Optional[protobug.String] = protobug.field(80)
    chipset: typing.Optional[protobug.String] = protobug.field(92)
    gl_device_info: typing.Optional[GLDeviceInfo] = protobug.field(102)


@protobug.message
class Fqa:
    type: typing.Optional[protobug.Int32] = protobug.field(1)
    value: typing.Optional[protobug.Bytes] = protobug.field(2)


@protobug.message
class Hqa:
    code: typing.Optional[protobug.Int32] = protobug.field(1)
    message: typing.Optional[protobug.String] = protobug.field(2)


@protobug.message
class Gqa:
    field1: typing.Optional[protobug.Bytes] = protobug.field(1)
    field2: typing.Optional[Hqa] = protobug.field(2)


@protobug.message
class StreamerContext:
    client_info: ClientInfo = protobug.field(1)
    po_token: typing.Optional[protobug.Bytes] = protobug.field(2)
    playback_cookie: typing.Optional[protobug.Bytes] = protobug.field(3)
    gp: typing.Optional[protobug.Bytes] = protobug.field(4)
    field5: list[Fqa] = protobug.field(5)
    field6: list[protobug.Int32] = protobug.field(6)
    field7: typing.Optional[protobug.String] = protobug.field(7)
    field8: Gqa = protobug.field(8)


"""

message StreamerContext {
  message ClientInfo {
    optional string device_make = 12;
    optional string device_model = 13;
    optional int32 client_name = 16;
    optional string client_version = 17;
    optional string os_name = 18;
    optional string os_version = 19;
    optional string accept_language = 21;
    optional string accept_region = 22;
    optional int32 screen_width_points = 37;
    optional int32 screen_height_points = 38;
    optional float screen_width_inches = 39;
    optional float screen_height_inches = 40;
    optional int32 screen_pixel_density = 41;
    optional ClientFormFactor client_form_factor = 46;
    optional int32 gmscore_version_code = 50; // e.g. 243731017
    optional int32 window_width_points = 55;
    optional int32 window_height_points = 56;
    optional int32 android_sdk_version = 64;
    optional float screen_density_float = 65;
    optional int64 utc_offset_minutes = 67;
    optional string time_zone = 80;
    optional string chipset = 92; // e.g. "qcom;taro" 
    optional GLDeviceInfo gl_device_info = 102;
  }

  enum ClientFormFactor {
    UNKNOWN_FORM_FACTOR = 0;
    FORM_FACTOR_VAL1 = 1;
    FORM_FACTOR_VAL2 = 2;
  }

  message GLDeviceInfo {
    optional string gl_renderer = 1;
    optional int32 gl_es_version_major = 2;
    optional int32 gl_es_version_minor = 3;
  }

  message Fqa {
    optional int32 type = 1;
    optional bytes value = 2;
  }

  message Gqa {
    message Hqa {
      optional int32 code = 1;
      optional string message = 2;
    }

    optional bytes field1 = 1;
    optional Hqa field2 = 2;
  }

  optional ClientInfo client_info = 1;
  optional bytes po_token = 2;
  optional bytes playback_cookie = 3;
  optional bytes gp = 4;
  repeated Fqa field5 = 5;
  repeated int32 field6 = 6;
  optional string field7 = 7;
  optional Gqa field8 = 8;
}
"""