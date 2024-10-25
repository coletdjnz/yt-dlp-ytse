from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.utils import update_url_query


class _YTSE(YoutubeIE, plugin_name='YTSE'):

    def _list_formats(self, video_id, microformats, video_details, player_responses, player_url, duration=None):
        live_broadcast_details, live_status, streaming_data, formats, subtitles = super()._list_formats(video_id, microformats, video_details, player_responses, player_url, duration)

        format_types = self._configuration_arg('formats')

        if 'ump' in format_types or 'duplicate' in format_types:
            ump_formats = []
            for f in formats:
                if f.get('protocol') not in ('https', None):
                    continue
                format_copy = f.copy()
                format_copy['protocol'] = 'ump'
                format_copy['url'] = update_url_query(format_copy['url'], {'ump': 1, 'srfvp': 1})
                ump_formats.append(format_copy)

            formats.extend(ump_formats)

        return live_broadcast_details, live_status, streaming_data, formats, subtitles


import yt_dlp.downloader
from yt_dlp_plugins.extractor._umpfd import UMPFD

yt_dlp.downloader.PROTOCOL_MAP['ump'] = UMPFD

