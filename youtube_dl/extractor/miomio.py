# coding: utf-8
from __future__ import unicode_literals

import random

from .common import InfoExtractor
from ..utils import (
    xpath_text,
    int_or_none,
)


class MioMioIE(InfoExtractor):
    IE_NAME = 'miomio.tv'
    _VALID_URL = r'https?://(?:www\.)?miomio\.tv/watch/cc(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://www.miomio.tv/watch/cc179734/',
        'md5': '48de02137d0739c15b440a224ad364b9',
        'info_dict': {
            'id': '179734',
            'ext': 'flv',
            'title': '手绘动漫鬼泣但丁全程画法',
            'duration': 354,
        },
    }, {
        'url': 'http://www.miomio.tv/watch/cc184024/',
        'info_dict': {
            'id': '43729',
            'title': '《动漫同人插画绘制》',
        },
        'playlist_mincount': 86,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._html_search_meta(
            'description', webpage, 'title', fatal=True)

        mioplayer_path = self._search_regex(
            r'src="(/mioplayer/[^"]+)"', webpage, 'ref_path')

        xml_config = self._search_regex(
            r'flashvars="type=sina&amp;(.+?)&amp;',
            webpage, 'xml config')

        # skipping the following page causes lags and eventually connection drop-outs
        self._request_webpage(
            'http://www.miomio.tv/mioplayer/mioplayerconfigfiles/xml.php?id=%s&r=%s' % (id, random.randint(100, 999)),
            video_id)

        # the following xml contains the actual configuration information on the video file(s)
        vid_config = self._download_xml(
            'http://www.miomio.tv/mioplayer/mioplayerconfigfiles/sina.php?{0}'.format(xml_config),
            video_id)

        http_headers = {
            'Referer': 'http://www.miomio.tv%s' % mioplayer_path,
        }

        entries = []
        for f in vid_config.findall('./durl'):
            segment_url = xpath_text(f, 'url', 'video url')
            if not segment_url:
                continue
            order = xpath_text(f, 'order', 'order')
            segment_id = video_id
            segment_title = title
            if order:
                segment_id += '-%s' % order
                segment_title += ' part %s' % order
            entries.append({
                'id': segment_id,
                'url': segment_url,
                'title': segment_title,
                'duration': int_or_none(xpath_text(f, 'length', 'duration'), 1000),
                'http_headers': http_headers,
            })

        if len(entries) == 1:
            segment = entries[0]
            segment['id'] = video_id
            segment['title'] = title
            return segment

        return {
            '_type': 'multi_video',
            'id': video_id,
            'entries': entries,
            'title': title,
            'http_headers': http_headers,
        }
