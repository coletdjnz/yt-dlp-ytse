import typing
import protobug

@protobug.message
class FormatId:
  itag: typing.Optional[protobug.Int32] = protobug.field(1)
  last_modified: typing.Optional[protobug.UInt64] = protobug.field(2, default=None)
  xtags: typing.Optional[protobug.String] = protobug.field(3, default=None)

