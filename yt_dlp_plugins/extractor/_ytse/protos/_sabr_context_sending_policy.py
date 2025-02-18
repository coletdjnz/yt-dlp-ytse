import protobug


@protobug.message
class SabrContextSendingPolicy:
    # These contain the SabrContextUpdate.type values
    # They are used to alter if a SabrContextUpdate is sent or not?

    # Start sending the SabrContextUpdates of this type
    start_policy: list[protobug.Int32] = protobug.field(1, default_factory=list)

    # Stop sending the SabrContextUpdates of this type
    stop_policy: list[protobug.Int32] = protobug.field(2, default_factory=list)

    # Stop and discard the SabrContextUpdates of this type
    # When type of 3, something is cleared from video data (related to SSAP and TIMELINE_CONTEXT)
    discard_policy: list[protobug.Int32] = protobug.field(3, default_factory=list)
