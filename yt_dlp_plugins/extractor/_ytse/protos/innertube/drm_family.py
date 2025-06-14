import protobug
class DrmFamily(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    UNKNOWN = 0
    FLASHACCESS = 1
    WIDEVINE_CLASSIC = 2
    CLEARKEY = 3
    WIDEVINE = 4
    PLAYREADY = 5
    FAIRPLAY = 6
