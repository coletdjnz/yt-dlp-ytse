import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.innertube.client_info import ClientInfo


@protobug.message
class SabrContext:
    # Type and Value from a SabrContextUpdate
    type: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    value: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)


@protobug.message
class UnknownMessage1:
    code: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    message: typing.Optional[protobug.String] = protobug.field(2, default=None)


@protobug.message
class UnknownMessage2:
    unknown_field_1: typing.Optional[protobug.Bytes] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[UnknownMessage1] = protobug.field(2, default=None)


@protobug.message
class StreamerContext:
    client_info: typing.Optional[ClientInfo] = protobug.field(1, default=None)
    po_token: typing.Optional[protobug.Bytes] = protobug.field(2, default=None)
    playback_cookie: typing.Optional[protobug.Bytes] = protobug.field(3, default=None)
    unknown_field_4: typing.Optional[protobug.Bytes] = protobug.field(4, default=None)
    # referred to as "stmctxt". Seems to be the SABR context updates to apply?
    sabr_contexts: list[SabrContext] = protobug.field(5, default_factory=list)
    # referred to as "unsntctxt". Is the type in the SABR Context update that was not sent (e.g. sendByDefault is False, or excluded by a sending policy)
    unsent_sabr_contexts: list[protobug.Int32] = protobug.field(6, default_factory=list)
    unknown_field_7: typing.Optional[protobug.String] = protobug.field(7, default=None)
    unknown_field_8: typing.Optional[UnknownMessage2] = protobug.field(8, default=None)
