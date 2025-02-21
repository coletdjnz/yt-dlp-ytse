import typing
import protobug


@protobug.message
class DrmCapabilities:
    supports_widevine_l1: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    supports_widevine_l3: typing.Optional[protobug.Bool] = protobug.field(2, default=None)
    supports_fairplay: typing.Optional[protobug.Bool] = protobug.field(3, default=None)
    supports_playready: typing.Optional[protobug.Bool] = protobug.field(4, default=None)
    supports_hdcp: typing.Optional[protobug.Bool] = protobug.field(5, default=None)


@protobug.message
class SpatialAudioCapabilities:
    supports_multichannel_spatial_audio: typing.Optional[protobug.Bool] = protobug.field(1, default=None)
    supports_stereo_spatial_audio: typing.Optional[protobug.Bool] = protobug.field(2, default=None)


@protobug.message
class VideoFormatCapability:
    class Profile(protobug.Enum):
        UNKNOWN_PROFILE = 0
        MPEG4_SIMPLE = 1
        MPEG4_SIMPLE_0 = 2
        INTERMEDIATE = 3
        AVC_BASELINE = 4
        AVC_BASELINE_30 = 5
        AVC_BASELINE_31 = 6
        AVC_MAIN = 7
        AVC_MAIN_31 = 8
        AVC_HIGH = 9
        AVC_HIGH_30 = 10
        AVC_HIGH_31 = 11
        AVC_HIGH_32 = 12
        AVC_HIGH_41 = 13

    class VideoCodec(protobug.Enum):
        UNKNOWN_CODEC = 0
        H263 = 1
        H264 = 2
        VP8 = 3
        VP9 = 4
        H262 = 5
        VP6 = 6
        MPEG4 = 7
        AV1 = 8
        H265 = 9
        FLV1 = 10

    video_codec: typing.Optional[VideoCodec] = protobug.field(1, default=None)
    efficient: typing.Optional[protobug.Bool] = protobug.field(2, default=None)
    max_height: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    max_width: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    min_height: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    min_width: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    max_portrait_height: typing.Optional[protobug.Int32] = protobug.field(7, default=None)
    max_portrait_width: typing.Optional[protobug.Int32] = protobug.field(8, default=None)
    min_portrait_height: typing.Optional[protobug.Int32] = protobug.field(9, default=None)
    min_portrait_width: typing.Optional[protobug.Int32] = protobug.field(10, default=None)
    max_framerate: typing.Optional[protobug.Int32] = protobug.field(11, default=None)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    profiles_supported: list[Profile] = protobug.field(13, default_factory=list)
    drm_capabilities: typing.Optional[DrmCapabilities] = protobug.field(14, default=None)
    is_10_bit_supported: typing.Optional[protobug.Bool] = protobug.field(15, default=None)
    drm_capability: typing.Optional[protobug.Int32] = protobug.field(16, default=None)


@protobug.message
class AudioFormatCapability:

    class AudioCodec(protobug.Enum):
        UNKNOWN_CODEC = 0
        AAC = 1
        VORBIS = 2
        OPUS = 3
        DTSHD = 4
        EAC3 = 5
        PCM = 6
        AC3 = 7
        SPEEX = 8
        MP3 = 9
        MP2 = 10
        AMR = 11
        IAMF = 12
        XHEAAC = 13

    audio_codec: typing.Optional[AudioCodec] = protobug.field(1, default=None)
    num_channels: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    max_bitrate_bps: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    spatial_audio_capabilities: typing.Optional[SpatialAudioCapabilities] = protobug.field(4, default=None)
    drm_capability: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    spatial_capability_bitmask: typing.Optional[protobug.Int32] = protobug.field(6, default=None)


@protobug.message
class PerPlaybackAttributes:
    itag_deny_list: list[protobug.Int32] = protobug.field(1, default_factory=list)


@protobug.message
class MediaCapabilities:
    class HdrTransferFunctions(protobug.Enum):
        HDR_TRANSFER_FUNCTION_UNKNOWN = 0
        HDR_TRANSFER_FUNCTION_HLG = 1
        HDR_TRANSFER_FUNCTION_HDR_10 = 2
        HDR_TRANSFER_FUNCTION_HDR_10_PLUS = 3

    video_format_capabilities: list[VideoFormatCapability] = protobug.field(1, default_factory=list)
    audio_format_capabilities: list[AudioFormatCapability] = protobug.field(2, default_factory=list)
    hdr_transfer_functions: typing.Optional[HdrTransferFunctions] = protobug.field(3, default=None)
    per_playback_attributes: typing.Optional[PerPlaybackAttributes] = protobug.field(4, default=None)
    hdr_mode_bitmask: typing.Optional[protobug.Int32] = protobug.field(5, default=None)

