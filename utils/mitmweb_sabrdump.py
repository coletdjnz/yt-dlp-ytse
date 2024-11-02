import base64
import io

import protobug
from mitmproxy import http
from yt_dlp.networking import Response

from yt_dlp_plugins.extractor._ytse.downloader.sabr import UMPParser
from yt_dlp_plugins.extractor._ytse.protos import MediaHeader, SabrRedirect, NextRequestPolicy, \
    FormatInitializationMetadata, StreamProtectionStatus, VideoPlaybackAbrRequest, PlaybackStartPolicy, RequestCancellationPolicy, SabrSeek
from yt_dlp_plugins.extractor._ytse.ump import UMPPartType



last_start_time = 0

class UMPDecoder:
    def response(self, flow: http.HTTPFlow) -> None:
        global last_start_time
        if "application/vnd.yt-ump" in flow.response.headers.get("Content-Type", ""):
            res = Response(fp=io.BytesIO(flow.response.raw_content), url=flow.request.url, headers={})
            parser = UMPParser(res)
            # get "rn" parameter from url
            rn = flow.request.query.get("rn")

            with open(f'dumps/{rn}.dump', 'w') as f, open(f'dumps/{rn}-processed.dump', 'w') as p:
                f.write(f'URL: {flow.request.url}\n')
                p.write(f'URL: {flow.request.url}\n')
                f.write(f'request body base64: {base64.b64encode(flow.request.raw_content).decode("utf-8")}\n')
                vpar = protobug.loads(flow.request.raw_content, VideoPlaybackAbrRequest)
                f.write(f'request body decoded: {vpar}\n')

                start_time_ms = vpar.client_abr_state.start_time_ms
                buffered_ranges = vpar.buffered_ranges

                p.write(f'Start Time: {start_time_ms} (+{start_time_ms - last_start_time})\n')
                p.write(f'Buffered Ranges: {buffered_ranges}\n')


                last_start_time = start_time_ms

                for part in parser.iter_parts():
                    print(f'Part type: {part.part_type}, Part size: {part.size}')
                    f.write(
                        f'Part type: {part.part_type} ({part.part_type.name}), Part size: {part.size}\n')

                    if part.part_type != UMPPartType.MEDIA:
                        f.write(f'Part data base64: {part.get_b64_str()}\n')

                    if part.part_type == UMPPartType.MEDIA_HEADER:
                        media_header = protobug.loads(part.data, MediaHeader)
                        f.write(f'Media Header: {media_header}\n')
                        p.write(f'Media Header itag {media_header.itag}: duration_ms={media_header.duration_ms} seq={media_header.sequence_number} tr={media_header.time_range}\n')

                    elif part.part_type == UMPPartType.SABR_REDIRECT:
                        f.write(f'SABR Redirect: {protobug.loads(part.data, SabrRedirect)}\n')

                    elif part.part_type == UMPPartType.NEXT_REQUEST_POLICY:
                        f.write(f'Next Request Policy: {protobug.loads(part.data, NextRequestPolicy)}\n')
                        p.write(f'Next Request Policy: {protobug.loads(part.data, NextRequestPolicy)}\n')

                    elif part.part_type == UMPPartType.FORMAT_INITIALIZATION_METADATA:
                        f.write(f'Format Initialization Metadata {protobug.loads(part.data, FormatInitializationMetadata)}\n')

                    elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                        f.write(f'Stream Protection Status: {protobug.loads(part.data, StreamProtectionStatus)}\n')

                    elif part.part_type == UMPPartType.PLAYBACK_START_POLICY:
                        f.write(f'Playback Start Policy: {protobug.loads(part.data, PlaybackStartPolicy)}\n')
                        p.write(f'Playback Start Policy: {protobug.loads(part.data, PlaybackStartPolicy)}\n')

                    elif part.part_type == UMPPartType.REQUEST_CANCELLATION_POLICY:
                        f.write(f'Request Cancellation Policy: {protobug.loads(part.data, RequestCancellationPolicy)}\n')
                        p.write(f'Request Cancellation Policy: {protobug.loads(part.data, RequestCancellationPolicy)}\n')

                    elif part.part_type == UMPPartType.SABR_SEEK:
                        f.write(f'Sabr Seek: {protobug.loads(part.data, SabrSeek)}\n')
                        p.write(f'Sabr Seek: {protobug.loads(part.data, SabrSeek)}\n')

                    elif part.part_type == UMPPartType.MEDIA or part.part_type == UMPPartType.MEDIA_END:
                        f.write(f'Media Header Id: {part.data[0]}\n')



addons = [
    UMPDecoder()
]