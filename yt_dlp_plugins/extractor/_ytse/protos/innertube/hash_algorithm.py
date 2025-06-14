import protobug

class HashAlgorithm(protobug.Enum, strict=False):
    # Unconfirmed proto mapping
    HASH_ALGORITHM_UNKNOWN = 0
    HASH_ALGORITHM_SHA256 = 1
    HASH_ALGORITHM_BLOCKS_SHA256 = 2
    HASH_ALGORITHM_STREAM_KEY_SHA256 = 3