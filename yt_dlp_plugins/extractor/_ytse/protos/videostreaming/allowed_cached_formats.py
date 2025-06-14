import protobug
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_id import FormatId


@protobug.message
class AllowedCachedFormats:
    allowed_cached_formats: list[FormatId] = protobug.field(1, default_factory=list)
