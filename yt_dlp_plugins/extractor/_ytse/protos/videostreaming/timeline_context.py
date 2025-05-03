import typing
import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_context_update import SabrContextUpdate


@protobug.message
class UnknownMessage1:
    video_id: typing.Optional[protobug.String] = protobug.field(1, default=None) # videoId
    pst: typing.Optional[protobug.Int32] = protobug.field(2, default=None)  # time - playback start time?
    lst: typing.Optional[protobug.Int32] = protobug.field(3, default=None) # lst
    ld: typing.Optional[protobug.Int32] = protobug.field(4, default=None) # duration
    ls: typing.Optional[protobug.Int32] = protobug.field(5, default=None) # scale for ld
    ps: typing.Optional[protobug.Int32] = protobug.field(6, default=None) # scale for pst



@protobug.message
class UnknownMessage2:
    unknown_field_1: typing.Optional[protobug.Int32] = protobug.field(1, default=None) # "nonv"


@protobug.message
class Clip:
    clip_id: typing.Optional[protobug.String] = protobug.field(1, default=None)
    unknown_field_2: typing.Optional[UnknownMessage1] = protobug.field(2, default=None)
    unknown_field_3: typing.Optional[UnknownMessage2] = protobug.field(3, default=None)


@protobug.message
class Timeline:
    clip: list[Clip] = protobug.field(1, default_factory=list)
    version: typing.Optional[protobug.String] = protobug.field(2, default=None)


# Looks like this may be used for SSAP to update the visible timeline + provide a SABR context override to switch to the ad?
@protobug.message
class TimelineContext:
    timeline: typing.Optional[Timeline] = protobug.field(1, default=None)
    sabr_context_update: typing.Optional[SabrContextUpdate] = protobug.field(2, default=None)
