import typing
import protobug
from . import SabrContextUpdate


@protobug.message
class rkH:
    video_id: typing.Optional[protobug.String] = protobug.field(1, default=None) # videoId
    Xn: typing.Optional[protobug.Int32] = protobug.field(2, default=None)  # pst (playback start time?)
    ZJ2: typing.Optional[protobug.Int32] = protobug.field(3, default=None) # lst (last seen time?)
    sj: typing.Optional[protobug.Int32] = protobug.field(4, default=None) # ld (load duration?)
    GU: typing.Optional[protobug.Int32] = protobug.field(5, default=None) # ls (last seen?)
    wE: typing.Optional[protobug.Int32] = protobug.field(6, default=None) # ps (playback speed/state?)



@protobug.message
class i8V:
    L4: typing.Optional[protobug.Int32] = protobug.field(1, default=None) # nonv


@protobug.message
class Clip:
    clip_id: typing.Optional[protobug.String] = protobug.field(1, default=None)
    T7: typing.Optional[rkH] = protobug.field(2, default=None)
    h2: typing.Optional[i8V] = protobug.field(3, default=None)


@protobug.message
class Timeline:
    clip: list[Clip] = protobug.field(1, default_factory=list)
    version: typing.Optional[protobug.String] = protobug.field(2, default=None)


@protobug.message
class TimelineContext:
    timeline: typing.Optional[Timeline] = protobug.field(1, default=None)  # may be a list, todo: confirm
    sabr_context_update: typing.Optional[SabrContextUpdate] = protobug.field(2, default=None)
