import typing
import protobug
from .audio_quality import AudioQuality
from .audio_track import AudioTrack
from .caption_track import CaptionTrack
from .color_info import ColorInfo
from .drm_family import DrmFamily
from .drm_track_type import DrmTrackType
from .range import Range
from .signature_info import SignatureInfo


@protobug.message
class FormatStream:


    class ProjectionType(protobug.Enum, strict=False):
        UNKNOWN = 0
        RECTANGULAR = 1
        EQUIRECTANGULAR = 2
        EQUIRECTANGULAR_THREED_TOP_BOTTOM = 3
        MESH = 4


    class StereoLayout(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        STEREO_LAYOUT_UNKNOWN = 0
        STEREO_LAYOUT_LEFT_RIGHT = 1
        STEREO_LAYOUT_TOP_BOTTOM = 2


    class FormatStreamType(protobug.Enum, strict=False):
        FORMAT_STREAM_TYPE_UNKNOWN = 0
        FORMAT_STREAM_TYPE_OTF = 3


    class SpatialAudioType(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        SPATIAL_AUDIO_TYPE_NONE = 0
        SPATIAL_AUDIO_TYPE_AMBISONICS_5_1 = 1
        SPATIAL_AUDIO_TYPE_AMBISONICS_QUAD = 2
        SPATIAL_AUDIO_TYPE_FOA_WITH_NON_DIEGETIC = 3

    itag: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    url: typing.Optional[protobug.String] = protobug.field(2, default=None)

    mime_type: typing.Optional[protobug.String] = protobug.field(5, default=None)
    bitrate: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    width: typing.Optional[protobug.Int32] = protobug.field(7, default=None)
    height: typing.Optional[protobug.Int32] = protobug.field(8, default=None)
    init_range: typing.Optional[Range] = protobug.field(9, default=None)
    index_range: typing.Optional[Range] = protobug.field(10, default=None)
    last_modified: typing.Optional[protobug.Int64] = protobug.field(11, default=None)
    content_length: typing.Optional[protobug.Int64] = protobug.field(12, default=None)

    quality: typing.Optional[protobug.String] = protobug.field(16, default=None)

    xtags: typing.Optional[protobug.String] = protobug.field(23, default=None)
    drm_families: typing.Optional[DrmFamily] = protobug.field(24, default=None)
    fps: typing.Optional[protobug.Int32] = protobug.field(25, default=None)
    quality_label: typing.Optional[protobug.String] = protobug.field(26, default=None)
    projection_type: typing.Optional[ProjectionType] = protobug.field(27, default=None)
    audio_track: typing.Optional[AudioTrack] = protobug.field(28, default=None)

    average_bitrate: typing.Optional[protobug.Int32] = protobug.field(31, default=None)
    spatial_audio_type: typing.Optional[SpatialAudioType] = protobug.field(32, default=None)
    color_info: typing.Optional[ColorInfo] = protobug.field(33, default=None)
    signature_info: typing.Optional[SignatureInfo] = protobug.field(34, default=None)
    target_duration_sec: typing.Optional[protobug.Double] = protobug.field(35, default=None)
    fair_play_key_uri: typing.Optional[protobug.String] = protobug.field(36, default=None)
    stereo_layout: typing.Optional[StereoLayout] = protobug.field(37, default=None)
    max_dvr_duration_sec: typing.Optional[protobug.Double] = protobug.field(38, default=None)
    high_replication: typing.Optional[protobug.Bool] = protobug.field(39, default=None)

    type: typing.Optional[FormatStreamType] = protobug.field(41, default=None)
    caption_track: typing.Optional[CaptionTrack] = protobug.field(42, default=None)
    audio_quality: typing.Optional[AudioQuality] = protobug.field(43, default=None)
    approx_duration_ms: typing.Optional[protobug.UInt64] = protobug.field(44, default=None)
    audio_sample_rate: typing.Optional[protobug.UInt64] = protobug.field(45, default=None)
    audio_channels: typing.Optional[protobug.UInt32] = protobug.field(46, default=None)
    loudness_db: typing.Optional[protobug.Float] = protobug.field(47, default=None)
    signature_cipher: typing.Optional[protobug.String] = protobug.field(48, default=None)
    is_drc: typing.Optional[protobug.Bool] = protobug.field(49, default=None)
    drm_track_type: typing.Optional[DrmTrackType] = protobug.field(50, default=None)
    distinct_params: typing.Optional[protobug.String] = protobug.field(51, default=None)

    track_absolute_loudness_lkfs: typing.Optional[protobug.Float] = protobug.field(53, default=None)
    is_vb: typing.Optional[protobug.Bool] = protobug.field(54, default=None)

    # stereo_resolution: typing.Optional[StereoResolution] = protobug.field(??, default=None)  # proto mapping missing
    #  STEREO_RESOLUTION_UNKNOWN, STEREO_RESOLUTION_HALF, STEREO_RESOLUTION_FULL
