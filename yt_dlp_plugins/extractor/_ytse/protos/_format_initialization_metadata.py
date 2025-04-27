import typing
import protobug
from ._format_id import FormatId


@protobug.message
class InitRange:
    start: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    end: typing.Optional[protobug.Int32] = protobug.field(2, default=None)


@protobug.message
class IndexRange:
    start: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    end: typing.Optional[protobug.Int32] = protobug.field(2, default=None)


class ProjectionType(protobug.Enum, strict=False):
    RECTANGULAR = 1


class ColorPrimaries(protobug.Enum, strict=False):
    COLOR_PRIMARIES_BT709 = 1


class ColorTransferCharacteristics(protobug.Enum, strict=False):
    COLOR_TRANSFER_CHARACTERISTICS_BT709 = 1


class ColorMatrixCoefficients(protobug.Enum, strict=False):
    COLOR_MATRIX_COEFFICIENTS_BT709 = 1


@protobug.message
class ColorInfo:
    primaries: typing.Optional[ColorPrimaries] = protobug.field(1, default=None)
    transfer_characteristics: typing.Optional[ColorTransferCharacteristics] = protobug.field(2, default=None)
    matrix_coefficients: typing.Optional[ColorMatrixCoefficients] = protobug.field(3, default=None)


@protobug.message
class Format:
    itag: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    mime_type: typing.Optional[protobug.String] = protobug.field(5, default=None)
    bitrate: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    width: typing.Optional[protobug.Int32] = protobug.field(7, default=None)
    height: typing.Optional[protobug.Int32] = protobug.field(8, default=None)
    init_range: typing.Optional[InitRange] = protobug.field(9, default=None)
    index_range: typing.Optional[IndexRange] = protobug.field(10, default=None)
    last_modified: typing.Optional[protobug.UInt64] = protobug.field(11, default=None)
    content_length: typing.Optional[protobug.Int32] = protobug.field(12, default=None)
    quality: typing.Optional[protobug.String] = protobug.field(16, default=None)

    # field_23 = typing.Optional Message
    fps: typing.Optional[protobug.Int32] = protobug.field(25, default=None)
    quality_label: typing.Optional[protobug.String] = protobug.field(26, default=None)
    projection_type: typing.Optional[ProjectionType] = protobug.field(27, default=None)
    average_bitrate: typing.Optional[protobug.Int32] = protobug.field(31, default=None)
    color_info: typing.Optional[ColorInfo] = protobug.field(33, default=None)

    # field 43 = 20
    approx_duration_ms: typing.Optional[protobug.UInt64] = protobug.field(44, default=None)
    # field 45 = 48000
    # field 45 = 2
    signature_cipher: typing.Optional[protobug.String] = protobug.field(48, default=None)
    # field 53 = large number


@protobug.message
class FormatInitializationMetadata:
    video_id: protobug.String = protobug.field(1, default=None)
    format_id: FormatId = protobug.field(2, default=None)
    end_time_ms: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    total_segments: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    mime_type: typing.Optional[protobug.String] = protobug.field(5, default=None)
    init_range: typing.Optional[InitRange] = protobug.field(6, default=None)
    index_range: typing.Optional[IndexRange] = protobug.field(7, default=None)
    format: typing.Optional[Format] = protobug.field(8, default=None)
    duration: typing.Optional[protobug.Int32] = protobug.field(9, default=None)
    duration_timescale: typing.Optional[protobug.Int32] = protobug.field(10, default=None)