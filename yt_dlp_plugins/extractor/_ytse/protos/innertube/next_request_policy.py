import typing
import protobug


@protobug.message
class NextRequestPolicy:
    target_audio_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(1, default=None)
    target_video_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    max_time_since_last_request_ms: typing.Optional[protobug.Int32] = protobug.field(3, default=None)
    backoff_time_ms: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    min_audio_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
    min_video_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(6, default=None)
    playback_cookie: typing.Optional[protobug.Bytes] = protobug.field(7, default=None)  # xxx: "PlaybackCookie" proto
    video_id: typing.Optional[protobug.String] = protobug.field(8, default=None)
