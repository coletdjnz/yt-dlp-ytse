import typing
import protobug

from ._seek_source import SeekSource


@protobug.message
class SabrSeek:
    start: typing.Optional[protobug.Int64] = protobug.field(1, default=None)
    timescale: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    seek_source: typing.Optional[SeekSource] = protobug.field(3, default=None)