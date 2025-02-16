import typing
import protobug
from ._buffered_range import BufferedRange


# @protobug.message
# class ContextUpdate:
#     # At least appears to match BufferedRange pb...
#     buffered_ranges: list[BufferedRange] = protobug.field(1, default_factory=list)

# May be used in:
# - mediaCommonConfig in Innertube config
# - SABR_CONTEXT_UPDATE
# - TIMELINE_CONTEXT

@protobug.message
class SabrContextUpdate:

    class SabrContextScope(protobug.Enum):
        SABR_CONTEXT_SCOPE_UNKNOWN = 0
        SABR_CONTEXT_SCOPE_PLAYBACK = 1
        SABR_CONTEXT_SCOPE_REQUEST = 2
        SABR_CONTEXT_SCOPE_WATCH_ENDPOINT = 3
        SABR_CONTEXT_SCOPE_CONTENT_ADS = 4

    class SabrContextWritePolicy(protobug.Enum):
        # Whether to override existing sabr context updates?
        SABR_CONTEXT_WRITE_POLICY_UNSPECIFIED = 0
        SABR_CONTEXT_WRITE_POLICY_OVERWRITE = 1
        SABR_CONTEXT_WRITE_POLICY_KEEP_EXISTING = 2

    type: typing.Optional[protobug.Int32] = protobug.field(1, default=None)  # seen = 2
    scope: typing.Optional[SabrContextScope] = protobug.field(2, default=None) # seen = 2 (SABR_CONTEXT_SCOPE_REQUEST?)

    # May be base64 encoded, but not always
    value: typing.Optional[protobug.Bytes] = protobug.field(3, default=None)
    send_by_default: typing.Optional[protobug.Bool] = protobug.field(4, default=None)  # seen = True
    write_policy: typing.Optional[SabrContextWritePolicy] = protobug.field(5, default=None)
