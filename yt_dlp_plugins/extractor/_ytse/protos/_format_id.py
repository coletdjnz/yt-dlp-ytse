import typing
import protobug


@protobug.message
class FormatId:
  itag: typing.Optional[protobug.Int32] = protobug.field(1)
  last_modified: typing.Optional[protobug.UInt64] = protobug.field(2, default=None)
  xtags: typing.Optional[protobug.String] = protobug.field(3, default=None)

  def __eq__(self, other):
    return self.itag == other.itag and self.last_modified == other.last_modified and self.xtags == other.xtags

