import protobug


@protobug.message
class SignatureInfo:
    pass
    # algorithm: typing.Optional[HashAlgorithm] = protobug.field(??, default=None) # proto mapping missing
    # ecdsa_signature: typing.Optional[protobug.String] = protobug.field(??, default=None) # proto mapping missing