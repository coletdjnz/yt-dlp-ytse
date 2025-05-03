import protobug
class DrmTrackType(protobug.Enum, strict=False):
    DRM_TRACK_TYPE_UNSPECIFIED = 0
    DRM_TRACK_TYPE_AUDIO = 1
    DRM_TRACK_TYPE_SD = 2
    DRM_TRACK_TYPE_HD = 3
    DRM_TRACK_TYPE_UHD1 = 4
    DRM_TRACK_TYPE_UHD2 = 5
