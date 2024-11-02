import base64
import io

import protobug
from mitmproxy import http
from yt_dlp.networking import Response

from yt_dlp_plugins.extractor._ytse.downloader.sabr import UMPParser
from yt_dlp_plugins.extractor._ytse.protos import MediaHeader, SabrRedirect, NextRequestPolicy, \
    FormatInitializationMetadata, StreamProtectionStatus, VideoPlaybackAbrRequest
from yt_dlp_plugins.extractor._ytse.ump import UMPPartType


class UMPDecoder:
    def response(self, flow: http.HTTPFlow) -> None:
        if "application/vnd.yt-ump" in flow.response.headers.get("Content-Type", ""):
            res = Response(fp=io.BytesIO(flow.response.raw_content), url=flow.request.url, headers={})
            parser = UMPParser(res)
            # get "rn" parameter from url
            rn = flow.request.query.get("rn")
            with open(f'dumps/{rn}.dump', 'a') as f:
                f.write(f'URL: {flow.request.url}\n')
                f.write(f'request body base64: {base64.b64encode(flow.request.raw_content).decode("utf-8")}\n')
                f.write(f'request body decoded: {protobug.loads(flow.request.raw_content, VideoPlaybackAbrRequest)}\n')
                for part in parser.iter_parts():
                    print(f'Part type: {part.part_type}, Part size: {part.size}')
                    f.write(
                        f'Part type: {part.part_type} ({part.part_type.name}), Part size: {part.size}\n')

                    if part.part_type != UMPPartType.MEDIA:
                        f.write(f'Part data base64: {part.get_b64_str()}\n')

                    if part.part_type == UMPPartType.MEDIA_HEADER:
                        f.write(f'Media Header: {protobug.loads(part.data, MediaHeader)}\n')

                    elif part.part_type == UMPPartType.SABR_REDIRECT:
                        f.write(f'SABR Redirect: {protobug.loads(part.data, SabrRedirect)}\n')

                    elif part.part_type == UMPPartType.NEXT_REQUEST_POLICY:
                        f.write(f'Next Request Policy: {protobug.loads(part.data, NextRequestPolicy)}\n')

                    elif part.part_type == UMPPartType.FORMAT_INITIALIZATION_METADATA:
                        f.write(f'Format Initialization Metadata {protobug.loads(part.data, FormatInitializationMetadata)}\n')

                    elif part.part_type == UMPPartType.STREAM_PROTECTION_STATUS:
                        f.write(f'Stream Protection Status: {protobug.loads(part.data, StreamProtectionStatus)}\n')

addons = [
    UMPDecoder()
]