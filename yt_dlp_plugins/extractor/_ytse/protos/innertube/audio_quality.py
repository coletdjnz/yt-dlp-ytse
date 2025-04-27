import protobug
class AudioQuality(protobug.Enum, strict=False):
    AUDIO_QUALITY_UNKNOWN = 0
    AUDIO_QUALITY_ULTRALOW = 5
    AUDIO_QUALITY_LOW = 10
    AUDIO_QUALITY_MEDIUM = 20
    AUDIO_QUALITY_HIGH = 30
