import typing
import protobug


@protobug.message
class VideoFormatCapability:
    video_codec: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    max_height: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    max_width: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    max_framerate: typing.Optional[protobug.Int32] = protobug.field(11, default=None)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    is_10_bit_supported: typing.Optional[protobug.Bool] = protobug.field(15, default=None)


@protobug.message
class AudioFormatCapability:
    audio_codec: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    num_channels: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    spatial_capability_bitmask: typing.Optional[protobug.Int32] = protobug.field(6, default=None)


@protobug.message
class MediaCapabilities:
    video_format_capabilities: list[VideoFormatCapability] = protobug.field(1)
    audio_format_capabilities: list[AudioFormatCapability] = protobug.field(2)
    hdr_mode_bitmask: typing.Optional[protobug.Int32] = protobug.field(5, default=None)