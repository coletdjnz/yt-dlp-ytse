import typing
import protobug

from yt_dlp_plugins.extractor._ytse.protos.innertube.seek_source import SeekSource


@protobug.message
class SabrSeek:
    seek_time_ticks: protobug.Int32 = protobug.field(1)
    timescale: protobug.Int32 = protobug.field(2)
    seek_source: typing.Optional[SeekSource] = protobug.field(3, default=None)