# usage: PYTHONPATH="." python utils/read_sabr_response.py /path/to/file


import base64
import io
import sys

import protobug
from mitmproxy import http
from yt_dlp.networking import Response
from yt_dlp_plugins.extractor._ytse.protos import unknown_fields

from yt_dlp_plugins.extractor._ytse.protos.videostreaming.media_header import MediaHeader
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.live_metadata import LiveMetadata
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.stream_protection_status import StreamProtectionStatus
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_redirect import SabrRedirect
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.format_initialization_metadata import FormatInitializationMetadata
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_seek import SabrSeek
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_error import SabrError
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.request_cancellation_policy import RequestCancellationPolicy
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.selectable_formats import SelectableFormats
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.prewarm_connection import PrewarmConnection
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.allowed_cached_formats import AllowedCachedFormats
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_context_update import SabrContextUpdate
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.sabr_context_sending_policy import SabrContextSendingPolicy
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.timeline_context import TimelineContext
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.reload_player_response import ReloadPlayerResponse
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.snackbar_message import SnackbarMessage
from yt_dlp_plugins.extractor._ytse.protos.videostreaming.playback_debug_info import PlaybackDebugInfo

from yt_dlp_plugins.extractor._ytse.protos.innertube.next_request_policy import NextRequestPolicy
from yt_dlp_plugins.extractor._ytse.protos.innertube.playback_start_policy import PlaybackStartPolicy
from yt_dlp_plugins.extractor._ytse.ump import UMPPartType, UMPParser


def write_unknown_fields(f, protobug_obj):
    uf = list(unknown_fields(protobug_obj))
    if uf:
        print(f'Unknown Fields: {uf}')


def print_sabr_parts(fp):
    res = Response(fp=fp, url='sabr:', headers={})
    parser = UMPParser(res)

    for part in parser.iter_parts():
        print(
            f'Part type: {part.part_type} ({part.part_type.name}:{part.part_id}), Part size: {part.size}')

        if part.part_type != UMPPartType.MEDIA:
            print(f'Part data base64: {part.get_b64_str()}')

        if part.part_type == UMPPartType.MEDIA_HEADER:
            media_header = protobug.loads(part.data, MediaHeader)
            print(f'Media Header: {media_header}')
            write_unknown_fields(f, media_header)

        elif part.part_type == UMPPartType.SABR_REDIRECT:
            sabr_redirect = protobug.loads(part.data, SabrRedirect)
            print(f'SABR Redirect: {sabr_redirect}')
            write_unknown_fields(f, sabr_redirect)

        elif part.part_type == UMPPartType.NEXT_REQUEST_POLICY:
            nrp = protobug.loads(part.data, NextRequestPolicy)
            print(f'Next Request Policy: {nrp}')
            write_unknown_fields(f, nrp)

        elif part.part_type == UMPPartType.FORMAT_INITIALIZATION_METADATA:
            fim = protobug.loads(part.data, FormatInitializationMetadata)
            print(f'Format Initialization Metadata {fim}')
            write_unknown_fields(f, fim)

        elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
            sps = protobug.loads(part.data, StreamProtectionStatus)
            print(f'Stream Protection Status: {sps}')
            write_unknown_fields(f, sps)

        elif part.part_type == UMPPartType.PLAYBACK_START_POLICY:
            psp = protobug.loads(part.data, PlaybackStartPolicy)
            print(f'Playback Start Policy: {psp}')
            write_unknown_fields(f, psp)

        elif part.part_type == UMPPartType.REQUEST_CANCELLATION_POLICY:
            rcp = protobug.loads(part.data, RequestCancellationPolicy)
            print(f'Request Cancellation Policy: {rcp}')
            write_unknown_fields(f, rcp)

        elif part.part_type == UMPPartType.SABR_SEEK:
            sabr_seek = protobug.loads(part.data, SabrSeek)
            print(f'Sabr Seek: {sabr_seek}')
            write_unknown_fields(f, sabr_seek)

        elif part.part_type == UMPPartType.LIVE_METADATA:
            lm = protobug.loads(part.data, LiveMetadata)
            print(f'Live Metadata: {lm}')
            write_unknown_fields(f, lm)

        elif part.part_type == UMPPartType.SELECTABLE_FORMATS:
            sf = protobug.loads(part.data, SelectableFormats)
            print(f'Selectable Formats: {sf}')
            write_unknown_fields(f, sf)

        elif part.part_type == UMPPartType.PREWARM_CONNECTION:
            pc = protobug.loads(part.data, PrewarmConnection)
            print(f'Prewarm Connection: {pc}')
            write_unknown_fields(f, pc)

        elif part.part_type == UMPPartType.ALLOWED_CACHED_FORMATS:
            acf = protobug.loads(part.data, AllowedCachedFormats)
            print(f'Allowed Cached Formats: {acf}')
            write_unknown_fields(f, acf)

        elif part.part_type == UMPPartType.SABR_CONTEXT_UPDATE:
            scu = protobug.loads(part.data, SabrContextUpdate)
            print(f'Sabr Context Update: {scu}')
            write_unknown_fields(f, scu)

        elif part.part_type == UMPPartType.SABR_CONTEXT_SENDING_POLICY:
            scsp = protobug.loads(part.data, SabrContextSendingPolicy)
            print(f'Sabr Context Sending Policy: {scsp}')
            write_unknown_fields(f, scsp)

        elif part.part_type == UMPPartType.TIMELINE_CONTEXT:
            tc = protobug.loads(part.data, TimelineContext)
            print(f'Timeline Context: {tc}')
            write_unknown_fields(f, tc)

        elif part.part_type == UMPPartType.RELOAD_PLAYER_RESPONSE:
            rpr = protobug.loads(part.data, ReloadPlayerResponse)
            print(f'Reload Player Response: {rpr}')
            write_unknown_fields(f, rpr)

        elif part.part_type == UMPPartType.PLAYBACK_DEBUG_INFO:
            pdi = protobug.loads(part.data, PlaybackDebugInfo)
            print(f'Playback Debug Info: {pdi}')
            write_unknown_fields(f, pdi)

        elif part.part_type == UMPPartType.SNACKBAR_MESSAGE:
            sm = protobug.loads(part.data, SnackbarMessage)
            print(f'Snackbar Message: {sm}')
            write_unknown_fields(f, sm)

        elif part.part_type == UMPPartType.SABR_ERROR:
            se = protobug.loads(part.data, SabrError)
            f.write(f'Sabr Error: {se}\n')
            write_unknown_fields(f, se)

        elif part.part_type == UMPPartType.MEDIA or part.part_type == UMPPartType.MEDIA_END:
            print(f'Media Header Id: {part.data[0]}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_sabr_response.py /path/to/file")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'rb') as f:
        print_sabr_parts(f)
        