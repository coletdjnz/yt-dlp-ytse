import protobug

class NetworkMeteredState(protobug.Enum, strict=False):
    NETWORK_METERED_STATE_UNKNOWN = 0
    NETWORK_METERED_STATE_UNMETERED = 1
    NETWORK_METERED_STATE_METERED = 2