import typing
import protobug


@protobug.message
class MinReadaheadPolicy:
    min_readahead_ms: typing.Optional[protobug.Int32] = protobug.field(2, default=None)
    min_bandwidth_bytes_per_sec: typing.Optional[protobug.Int32] = protobug.field(1, default=None)


@protobug.message
class PlaybackStartPolicy:
    start_min_readahead_policy: list[MinReadaheadPolicy] = protobug.field(1, default_factory=list)
    resume_min_readahead_policy: list[MinReadaheadPolicy] = protobug.field(2, default_factory=list)
    video_id: typing.Optional[protobug.String] = protobug.field(3, default=None)
    start_timeout_ms: typing.Optional[protobug.Int32] = protobug.field(4, default=None)
    resume_timeout_ms: typing.Optional[protobug.Int32] = protobug.field(5, default=None)
