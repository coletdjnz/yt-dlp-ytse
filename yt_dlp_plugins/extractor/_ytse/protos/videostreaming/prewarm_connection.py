import typing
import protobug

# This is the https://rrN---XX-XXXXXXXX.googlevideo.com/generate_204 url, used to open or keep the connection alive?
@protobug.message
class PrewarmConnection:
    prewarm_connection_url: typing.Optional[protobug.String] = protobug.field(1, default=None)
