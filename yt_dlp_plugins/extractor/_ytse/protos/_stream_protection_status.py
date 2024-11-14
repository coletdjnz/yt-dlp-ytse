import typing
import protobug


@protobug.message
class StreamProtectionStatus:

    class Status(protobug.Enum, strict=False):
        OK = 1
        ATTESTATION_PENDING = 2
        ATTESTATION_REQUIRED = 3

    status: typing.Optional[Status] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[protobug.UInt32] = protobug.field(2, default=None)
