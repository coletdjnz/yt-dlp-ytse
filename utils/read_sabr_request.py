# usage: PYTHONPATH="." python utils/read_sabr_request.py /path/to/file
import base64
import sys
from pprint import pprint

import protobug
from yt_dlp_plugins.extractor._ytse.protos import (
     unknown_fields,

)

from yt_dlp_plugins.extractor._ytse.protos.videostreaming.video_playback_abr_request import VideoPlaybackAbrRequest

def read_and_print_vpar(file_path):
    with open(file_path, 'rb') as f:
        file_content = f.read()

    try:
        vpar = protobug.loads(file_content, VideoPlaybackAbrRequest)
        pprint(vpar, width=120)
        print(f'video_playback_ustreamer_config b64: {base64.b64encode(vpar.video_playback_ustreamer_config).decode()}')
        print(f'ustream config base64: {base64.b64encode(vpar.video_playback_ustreamer_config).decode("utf-8")}\n')
        uf = list(unknown_fields(vpar))
        if uf:
            print(f'Unknown Fields: {uf}')
    except Exception as e:
        print(f'Error loading VideoPlaybackAbrRequest: {e}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_sabr_request.py /path/to/file")
        sys.exit(1)

    file_path = sys.argv[1]
    read_and_print_vpar(file_path)