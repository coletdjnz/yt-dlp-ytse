import typing
import protobug
from ._buffered_range import BufferedRange


@protobug.message
class ContextUpdate:
    # At least appears to match BufferedRange pb...
    buffered_ranges: list[BufferedRange] = protobug.field(1, default_factory=list)


@protobug.message
class SabrContextUpdate:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None)  # seen = 2
    unknown_field_2: typing.Optional[protobug.Int32] = protobug.field(2, default=None)  # seen = 2
    context_update: typing.Optional[ContextUpdate] = protobug.field(3, default_factory=ContextUpdate),
    unknown_field_4: typing.Optional[protobug.Int32] = protobug.field(4, default=None)  # seen = 1
