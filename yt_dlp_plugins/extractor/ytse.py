import re
import sys

from yt_dlp.extractor.openload import PhantomJSwrapper
from yt_dlp.extractor.youtube import (
    YoutubeIE,
    short_client_name,
    STREAMING_DATA_INITIAL_PO_TOKEN,
    STREAMING_DATA_CLIENT_NAME,
    _PoTokenContext
)
from yt_dlp.jsinterp import JSInterpreter
from yt_dlp.utils import (
    ExtractorError,
    NO_DEFAULT,
    determine_protocol,
    filesize_from_tbr,
    float_or_none,
    int_or_none,
    join_nonempty,
    mimetype2ext,
    parse_codecs,
    parse_qs,
    qualities,
    str_or_none,
    try_call,
    try_get,
    update_url_query,
)
from yt_dlp.utils.traversal import traverse_obj

import yt_dlp.downloader
from yt_dlp_plugins.extractor._ytse.downloader.ump import UMPFD
from yt_dlp_plugins.extractor._ytse.downloader.sabr import SABRFD


from yt_dlp.downloader import get_suitable_downloader as get_suitable_downloader_original, _get_suitable_downloader

yt_dlp.downloader.PROTOCOL_MAP['ump'] = UMPFD
yt_dlp.downloader.PROTOCOL_MAP['sabr'] = SABRFD


def get_suitable_downloader(info_dict, params={}, default=NO_DEFAULT, protocol=None, to_stdout=False):
    protocols = (protocol or determine_protocol(info_dict)).split('+')
    info_copy = info_dict.copy()
    info_copy['to_stdout'] = to_stdout

    downloaders = [_get_suitable_downloader(info_copy, proto, params, default) for proto in protocols]
    if set(downloaders) == {SABRFD} and SABRFD.can_download(info_copy):
        return SABRFD

    return get_suitable_downloader_original(info_dict, params, default, protocol, to_stdout)


sys.modules.get('yt_dlp.downloader').get_suitable_downloader = get_suitable_downloader
sys.modules.get('yt_dlp.YoutubeDL').get_suitable_downloader = get_suitable_downloader


class _YTSE(YoutubeIE, plugin_name='YTSE'):

    def _reload_sabr_config(self, video_id, client_name):
        url = 'https://www.youtube.com/watch?v=' + video_id
        _, _, prs, player_url = self._download_player_responses(url, dict(), video_id, url)
        video_details = traverse_obj(prs, (..., 'videoDetails'), expected_type=dict)
        microformats = traverse_obj(
            prs, (..., 'microformat', 'playerMicroformatRenderer'),
            expected_type=dict)
        _, live_status, _, formats, _ = self._list_formats(video_id, microformats, video_details, prs, player_url)

        for format in formats:
            if format.get('protocol') == 'sabr':
                sabr_config = format['_sabr_config']
                if sabr_config['client_name'] == client_name:
                    return format['url'], sabr_config['video_playback_ustreamer_config']

        raise ExtractorError('No SABR formats found', expected=True)

    def _process_n_param(self, gvs_url, video_id, player_url):
        query = parse_qs(gvs_url)
        if query.get('n'):
            try:
                return update_url_query(gvs_url, {'n': self._decrypt_nsig(query['n'][0], video_id, player_url)})
            except ExtractorError as e:
                phantomjs_hint = ''
                if isinstance(e, JSInterpreter.Exception):
                    phantomjs_hint = (
                        f'         Install {self._downloader._format_err("PhantomJS", self._downloader.Styles.EMPHASIS)} '
                        f'to workaround the issue. {PhantomJSwrapper.INSTALL_HINT}\n')
                if player_url:
                    self.report_warning(
                        f'nsig extraction failed: Some formats may be missing\n{phantomjs_hint}'
                        f'         n = {query["n"][0]} ; player = {player_url}', video_id=video_id, only_once=True)
                    self.write_debug(e, only_once=True)
                else:
                    self.report_warning(
                        'Cannot decrypt nsig without player_url: Some formats may be missing',
                        video_id=video_id, only_once=True)
        return gvs_url

    def _extract_sabr_formats(self, video_id, player_response, player_url, live_status, duration):
        # xxx: the upstream _extract_formats_and_subtitles should really be broken up into reusable functions
        formats = []

        # Extract SABR formats from one player response
        streaming_data = traverse_obj(player_response, 'streamingData')
        if not streaming_data:
            return formats

        server_abr_streaming_url = self._process_n_param(streaming_data.get('serverAbrStreamingUrl'), video_id, player_url)

        video_playback_ustreamer_config = traverse_obj(player_response, ('playerConfig', 'mediaCommonConfig', 'mediaUstreamerRequestConfig', 'videoPlaybackUstreamerConfig'))
        if not server_abr_streaming_url or not video_playback_ustreamer_config:
            return formats

        client_name = streaming_data.get(STREAMING_DATA_CLIENT_NAME)
        po_token = streaming_data.get(STREAMING_DATA_INITIAL_PO_TOKEN)

        sabr_config = {
            'video_playback_ustreamer_config': video_playback_ustreamer_config,
            'po_token': po_token,
            'client_name': client_name,
            'innertube_context': traverse_obj(player_response, 'responseContext'),
            'reload_config_fn': lambda: self._reload_sabr_config(video_id, client_name),
        }

        q = qualities([
            # Normally tiny is the smallest video-only formats. But
            # audio-only formats with unknown quality may get tagged as tiny
            'tiny',
            'audio_quality_ultralow', 'audio_quality_low', 'audio_quality_medium', 'audio_quality_high',  # Audio only formats
            'small', 'medium', 'large', 'hd720', 'hd1080', 'hd1440', 'hd2160', 'hd2880', 'highres',
        ])

        # Extract formats based on itag
        itag_qualities, res_qualities = {}, {0: None}
        original_language = None
        streaming_formats = traverse_obj(streaming_data, 'adaptiveFormats') or []
        PREFERRED_LANG_VALUE = 10
        for fmt in streaming_formats:
            # todo: pass down to SABRFD
            # if fmt.get('targetDurationSec'):
            #     continue

            itag = str_or_none(fmt.get('itag'))
            audio_track = fmt.get('audioTrack') or {}
            stream_id = (itag, audio_track.get('id'), fmt.get('isDrc'))

            quality = fmt.get('quality')
            height = int_or_none(fmt.get('height'))
            if quality == 'tiny' or not quality:
                quality = fmt.get('audioQuality', '').lower() or quality
            # The 3gp format (17) in android client has a quality of "small",
            # but is actually worse than other formats
            if itag == '17':
                quality = 'tiny'
            # if quality:
            #     if itag:
            #         itag_qualities[itag] = quality
            #     if height:
            #         res_qualities[height] = quality

            is_default = audio_track.get('audioIsDefault')
            is_descriptive = 'descriptive' in (audio_track.get('displayName') or '').lower()
            language_code = audio_track.get('id', '').split('.')[0]
            if language_code and is_default:
                original_language = language_code

            # FORMAT_STREAM_TYPE_OTF(otf=1) requires downloading the init fragment
            # (adding `&sq=0` to the URL) and parsing emsg box to determine the
            # number of fragment that would subsequently requested with (`&sq=N`)
            # todo: still relavant for SABR?
            # if fmt.get('type') == 'FORMAT_STREAM_TYPE_OTF':
            #     continue



            tbr = float_or_none(fmt.get('averageBitrate') or fmt.get('bitrate'), 1000)
            format_duration = traverse_obj(fmt, ('approxDurationMs', {lambda x: float_or_none(x, 1000)}))
            # Some formats may have much smaller duration than others (possibly damaged during encoding)
            # E.g. 2-nOtRESiUc Ref: https://github.com/yt-dlp/yt-dlp/issues/2823
            # Make sure to avoid false positives with small duration differences.
            # E.g. __2ABJjxzNo, ySuUZEjARPY
            is_damaged = try_call(lambda: format_duration < duration // 2)
            if is_damaged:
                self.report_warning(
                    f'{video_id}: Some formats are possibly damaged. They will be deprioritized', only_once=True)

            # Clients that require PO Token return videoplayback URLs that may return 403
            require_po_token = (
                    not po_token
                    and _PoTokenContext.GVS in self._get_default_ytcfg(client_name)['PO_TOKEN_REQUIRED_CONTEXTS']
                    and itag not in ['18'])  # these formats do not require PO Token

            if require_po_token and 'missing_pot' not in self._configuration_arg('formats'):
                self._report_pot_format_skipped(video_id, client_name, 'sabr')
                continue

            name = fmt.get('qualityLabel') or quality.replace('audio_quality_', '') or ''
            fps = int_or_none(fmt.get('fps')) or 0
            dct = {
                'asr': int_or_none(fmt.get('audioSampleRate')),
                'filesize': int_or_none(fmt.get('contentLength')),
                'format_id': f'{itag}{"-drc" if fmt.get("isDrc") else ""}',
                'format_note': join_nonempty(
                    join_nonempty(audio_track.get('displayName'), is_default and ' (default)', delim=''),
                    name, fmt.get('isDrc') and 'DRC',
                    try_get(fmt, lambda x: x['projectionType'].replace('RECTANGULAR', '').lower()),
                    try_get(fmt, lambda x: x['spatialAudioType'].replace('SPATIAL_AUDIO_TYPE_', '').lower()),
                    is_damaged and 'DAMAGED', require_po_token and 'MISSING POT',
                    (self.get_param('verbose')) and short_client_name(client_name),
                    delim=', '),
                'source_preference': -1 + (100 if 'Premium' in name else 0),
                'fps': fps if fps > 1 else None,  # For some formats, fps is wrongly returned as 1
                'audio_channels': fmt.get('audioChannels'),
                'height': height,
                'quality': q(quality) - bool(fmt.get('isDrc')) / 2,
                'has_drm': bool(fmt.get('drmFamilies')),
                'tbr': tbr,
                'filesize_approx': filesize_from_tbr(tbr, format_duration),
                'url': server_abr_streaming_url,
                'width': int_or_none(fmt.get('width')),
                'language': join_nonempty(language_code, 'desc' if is_descriptive else '') or None,
                'language_preference': PREFERRED_LANG_VALUE if is_default else -10 if is_descriptive else -1,
                # Strictly de-prioritize broken, damaged and 3gp formats
                'preference': -20 if require_po_token else -10 if is_damaged else -2 if itag == '17' else None,
                'protocol': 'sabr'
            }
            mime_mobj = re.match(
                r'((?:[^/]+)/(?:[^;]+))(?:;\s*codecs="([^"]+)")?', fmt.get('mimeType') or '')
            if mime_mobj:
                dct['ext'] = mimetype2ext(mime_mobj.group(1))
                dct.update(parse_codecs(mime_mobj.group(2)))
            single_stream = 'none' in (dct.get('acodec'), dct.get('vcodec'))
            if single_stream and dct.get('ext'):
                dct['container'] = dct['ext'] + '_dash'

            # Should not have both audio and video in one format
            if not single_stream:
                continue

            dct['is_from_start'] = live_status == 'is_live' and self.get_param('live_from_start')

            dct['_sabr_config'] = {
                **sabr_config,
                'itag': itag,
                'last_modified': fmt.get('lastModified'),
                'target_duration_sec': fmt.get('targetDurationSec'),
            }

            formats.append(dct)

        return formats

    def _prepare_live_from_start_formats(self, formats, *args, **kwargs):
        if traverse_obj(formats, (0, 'is_from_start')):
            return
        return super()._prepare_live_from_start_formats(formats, *args, **kwargs)

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

        if 'sabr' in format_types or 'duplicate' in format_types:
            formats = []
            for player_response in player_responses:
                formats.extend(self._extract_sabr_formats(video_id, player_response, player_url, live_status, duration))

        return live_broadcast_details, live_status, streaming_data, formats, subtitles
