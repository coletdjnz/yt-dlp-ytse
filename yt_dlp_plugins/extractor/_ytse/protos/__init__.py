import dataclasses
import typing
from ._stream_protection_status import StreamProtectionStatus
from ._media_header import MediaHeader
from ._sabr_error import SabrError
from ._sabr_redirect import SabrRedirect
from ._client_abr_state import ClientAbrState
from ._media_capabilities import MediaCapabilities, VideoFormatCapability, AudioFormatCapability
from ._video_playback_abr_request import VideoPlaybackAbrRequest
from ._playback_cookie import PlaybackCookie
from ._format_initialization_metadata import FormatInitializationMetadata
from ._next_request_policy import NextRequestPolicy
from ._playback_start_policy import PlaybackStartPolicy
from ._request_cancellation_policy import RequestCancellationPolicy
from ._sabr_seek import SabrSeek
from ._live_metadata import LiveMetadata
from ._buffered_range import BufferedRange
from ._format_id import FormatId
from ._streamer_context import StreamerContext, ClientInfo
from ._time_range import TimeRange
from ._selectable_formats import SelectableFormats
from ._prewarm_connection import PrewarmConnection
from ._allowed_cached_formats import AllowedCachedFormats
from ._sabr_context_update import SabrContextUpdate
from ._sabr_context_sending_policy import SabrContextSendingPolicy
from ._timeline_context import TimelineContext
from ._reload_player_response import ReloadPlayerResponse


def unknown_fields(obj: typing.Any, path=()) -> typing.Iterable[tuple[tuple[str, ...], dict[int, list]]]:
    if not dataclasses.is_dataclass(obj):
        return

    if unknown := getattr(obj, "_unknown", None):
        yield path, unknown

    for field in dataclasses.fields(obj):
        value = getattr(obj, field.name)
        yield from unknown_fields(value, (*path, field.name))