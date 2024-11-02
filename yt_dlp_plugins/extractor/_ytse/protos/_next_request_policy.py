import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos import PlaybackCookie

@protobug.message
class NextRequestPolicy:
    target_audio_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    target_video_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    backoff_time_ms: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    playback_cookie: typing.Optional[PlaybackCookie] = protobug.field(7, default=None)
    video_id: typing.Optional[protobug.String] = protobug.field(8, default=None)