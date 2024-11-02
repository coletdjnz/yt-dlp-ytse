import typing
import protobug


@protobug.message
class VideoFormatCapability:
    video_codec: typing.Optional[protobug.Int32] = protobug.field(1)
    max_height: typing.Optional[protobug.Int32] = protobug.field(3)
    max_width: typing.Optional[protobug.Int32] = protobug.field(4)
    max_framerate: typing.Optional[protobug.Int32] = protobug.field(11)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(12)
    is_10_bit_supported: typing.Optional[protobug.Bool] = protobug.field(15)


@protobug.message
class AudioFormatCapability:
    audio_codec: typing.Optional[protobug.Int32] = protobug.field(1)
    num_channels: typing.Optional[protobug.Int32] = protobug.field(2)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(3)
    spatial_capability_bitmask: typing.Optional[protobug.Int32] = protobug.field(6)


@protobug.message
class MediaCapabilities:
    video_format_capabilities: list[VideoFormatCapability] = protobug.field(1)
    audio_format_capabilities: list[AudioFormatCapability] = protobug.field(2)
    hdr_mode_bitmask: typing.Optional[protobug.Int32] = protobug.field(5)