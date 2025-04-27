import typing
import protobug


@protobug.message
class StreamProtectionStatus:

    class Status(protobug.Enum, strict=False):
        OK = 1
        ATTESTATION_PENDING = 2
        ATTESTATION_REQUIRED = 3

    status: typing.Optional[Status] = protobug.field(1, default=None)
    # Max. retries can make when status is ATTESTATION_REQUIRED
    # This is to give some extra time for the PO Token to be minted (as a last ditch effort)?
    max_retries: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
