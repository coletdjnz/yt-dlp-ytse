import typing
import protobug
@protobug.message
class ColorInfo:
    class Primaries(protobug.Enum, strict=False):
        COLOR_PRIMARIES_UNKNOWN = 0
        COLOR_PRIMARIES_BT709 = 1
        COLOR_PRIMARIES_UNSPECIFIED = 2
        COLOR_PRIMARIES_BT2020 = 9


    class TransferCharacteristics(protobug.Enum, strict=False):
        COLOR_TRANSFER_CHARACTERISTICS_UNKNOWN = 0
        COLOR_TRANSFER_CHARACTERISTICS_BT709 = 1
        COLOR_TRANSFER_CHARACTERISTICS_UNSPECIFIED = 2
        COLOR_TRANSFER_CHARACTERISTICS_BT2020_10 = 14
        COLOR_TRANSFER_CHARACTERISTICS_SMPTEST2084 = 16
        COLOR_TRANSFER_CHARACTERISTICS_ARIB_STD_B67 = 18


    class MatrixCoefficients(protobug.Enum, strict=False):
        COLOR_MATRIX_COEFFICIENTS_UNKNOWN = 0
        COLOR_MATRIX_COEFFICIENTS_BT709 = 1
        COLOR_MATRIX_COEFFICIENTS_UNSPECIFIED = 2
        COLOR_MATRIX_COEFFICIENTS_BT2020_NCL = 9


    class DynamicMetadata(protobug.Enum, strict=False):
        # Unconfirmed proto mapping
        DYNAMIC_METADATA_UNSPECIFIED = 0
        DYNAMIC_METADATA_SMPTE2094_40 = 1

    primaries: typing.Optional[Primaries] = protobug.field(1, default=None)
    transfer_characteristics: typing.Optional[TransferCharacteristics] = protobug.field(2, default=None)
    matrix_coefficients: typing.Optional[MatrixCoefficients] = protobug.field(3, default=None)
    dynamic_metadata: typing.Optional[DynamicMetadata] = protobug.field(4, default=None)
