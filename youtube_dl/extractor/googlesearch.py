from __future__ import unicode_literals

import itertools
import re

from .common import SearchInfoExtractor
from ..utils import (
    compat_urllib_parse,
)


class GoogleSearchIE(SearchInfoExtractor):
    IE_DESC = 'Google Video search'
    _MAX_RESULTS = 1000
    IE_NAME = 'video.google:search'
    _SEARCH_KEY = 'gvsearch'

    def _get_n_results(self, query, n):
        """Get a specified number of results for a query"""

        entries = []
        res = {
            '_type': 'playlist',
            'id': query,
            'title': query,
        }

        for pagenum in itertools.count():
            result_url = (
                'http://www.google.com/search?tbm=vid&q=%s&start=%s&hl=en'
                % (compat_urllib_parse.quote_plus(query), pagenum * 10))

            webpage = self._download_webpage(
                result_url, 'gvsearch:' + query,
                note='Downloading result page ' + str(pagenum + 1))

            for hit_idx, mobj in enumerate(re.finditer(
                    r'<h3 class="r"><a href="([^"]+)"', webpage)):

                # Skip playlists
                if not re.search(r'id="vidthumb%d"' % (hit_idx + 1), webpage):
                    continue

                entries.append({
                    '_type': 'url',
                    'url': mobj.group(1)
                })

            if (len(entries) >= n) or not re.search(r'id="pnnext"', webpage):
                res['entries'] = entries[:n]
                return res