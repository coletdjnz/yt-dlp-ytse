import typing
import protobug


# Seen on iOS SABR
# This is the https://rrN---XX-XXXXXXXX.googlevideo.com/generate_204 url, used to open or keep the connection alive?
@protobug.message
class PrewarmConnection:
    # XXX: this might be the same (or inherited from the same) protobuf object as SabrRedirect
    prewarm_connection_url: typing.Optional[protobug.String] = protobug.field(1, default=None)
