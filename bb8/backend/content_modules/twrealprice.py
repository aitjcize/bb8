# -*- coding: utf-8 -*-
"""
    Search for TW Real Price
    ~~~~~~~~~~~~~~~~~~~~~~~

    Provide Taiwan eState info.
"""

import cPickle
import datetime
import logging
import sqlite3
import time
import traceback
import urllib

from bb8.backend.module_api import (Config, Message, Memory, Resolve,
                                    SupportedPlatform)
import twrealprice_rule


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


GOOGLE_STATIC_MAP_API_KEY = 'AIzaSyCpP0pV9_YtQuV-Gzf6aL9nRt1Es5UlBv4'

# Maximum number of transaction to cache for "more data" feature.
MAX_CACHE_TRANS = 49  # 7 pages

# For lat/lng
GRID_NUM = 1000
LAT_MIN = 20.0
LAT_MAX = 26.0
LNG_MIN = 118.0
LNG_MAX = 123.0


def LatLngIndex(lat, lng):
    if lat < LAT_MIN or lat >= LAT_MAX:
        raise ValueError('Lat out of band: %.6f' % lat)
    if lng < LNG_MIN or lng >= LNG_MAX:
        raise ValueError('Lng out of band: %.6f' % lng)

    lat_step = (LAT_MAX - LAT_MIN) / GRID_NUM
    lng_step = (LNG_MAX - LNG_MIN) / GRID_NUM

    return (int((lat - LAT_MIN) / lat_step), int((lng - LNG_MIN) / lng_step))


def GenNearbyIndex(lat_center, lng_center, N):
    """Generate the nearby index of the given lat/lng index.

    Returns:
      lat_in, lng_in for the following sequence:

      3333333
      3222223
      3211123
      3210123
      3211123
      3222223
      3333333
    """
    n = 0
    yield (lat_center, lng_center)

    while n < N:
        n += 1
        for i in range(n * 2):                        # From left-top:
            yield lat_center - n + i, lng_center - n  # left --> right
        for i in range(n * 2):
            yield lat_center + n, lng_center - n + i  # top --> bottom
        for i in range(n * 2):
            yield lat_center + n - i, lng_center + n  # right --> left
        for i in range(n * 2):
            yield lat_center - n, lng_center + n - i  # bottom --> top


def RocSlash(roc_date):
    return '%s/%s/%s' % (roc_date[0:3], roc_date[3:5], roc_date[5:7])


def Age(build_date):
    try:
        return '%.f' % ((
            datetime.date.today() -
            twrealprice_rule.AdDate(build_date)).days / 365.0) + '年'
    except ValueError:
        return ''


def StreetOnly(s):
    sub = s['土地區段位置或建物區門牌'].split(s['鄉鎮市區'])
    if len(sub) == 2:
        return sub[1]
    return s['土地區段位置或建物區門牌']


def get_module_info():
    return {
        'id': 'ai.compose.content.third_party.twrealprice',
        'name': 'TwRealPrice',
        'description': 'estate info search according to location.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'twrealprice',
        'ui_module_name': 'twrealprice',
    }


def schema():
    return {
        'type': 'object',
        'required': ['api_key', 'max_count', 'location', 'distance_threshold'],
        'properties': {
            'api_key': {
                'type': 'string',
            },
            'max_count': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 100
            },
            'location': {
                'oneOf': [{
                    'type': 'string'
                }, {
                    'type': 'object',
                    'required': ['coordinates'],
                    'properties': {
                        'coordinates': {
                            'type': 'object',
                            'required': ['lat', 'long'],
                            'properties': {
                                'lat': {'type': 'number'},
                                'long': {'type': 'number'}
                            }
                        }
                    }
                }]
            },
            'distance_threshold': {'type': 'number'},
        }
    }


class GoogleStaticMapAPIRequestBuilder(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/staticmap'
    REDIRECT_URL = Config('HTTP_ROOT') + 'third_party/youbike/render_map?url='

    def __init__(self, api_key, size):
        self._api_key = api_key
        self._size = '%dx%d' % size
        self._maptype = 'roadmap'
        self._markers = {}

    def add_marker(self, coordinate, color='red'):
        self._markers[coordinate] = color

    def remove_marker(self, coordinate):
        del self._markers[coordinate]

    def clear_markers(self):
        self._markers = {}

    def _markers_string(self):
        return '&'.join(['markers=color:%s|%3.8f,%3.8f' %
                         ((color,) + coordinate)
                         for coordinate, color in self._markers.iteritems()])

    def build_url(self):
        url = ('%s?size=%s&maptype=%s&' %
               (self.API_ENDPOINT, self._size, self._maptype) +
               self._markers_string())
        return self.REDIRECT_URL + urllib.quote(url)

    @classmethod
    def build_navigation_url(cls, c):
        return 'http://maps.google.com/?daddr=%3.8f,%3.8f' % c


class TwRealPrice(object):
    def __init__(self):
        super(TwRealPrice, self).__init__()

    def nearby_transaction(self, max_count, coordinate, unused_threshold=0):

        db_files = [
            '/var/lib/twrealprice/twrealprice.db',
            '/var/lib/bb8/apps/twrealprice/resource/twrealprice.db',
        ]

        start_time = time.time()

        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                break
            except sqlite3.OperationalError:
                _LOG.warn('Database file is not found: %s', db_file)
        else:
            raise IOError(
                'Cannot find database in the following pathes: %s' %
                ', '.join(db_files))

        nearby = []
        try:
            lat_center, lng_center = LatLngIndex(coordinate[0], coordinate[1])
        except ValueError:
            traceback.print_exc()
            return [], []

        for lat_in, lng_in in GenNearbyIndex(lat_center, lng_center, 1):
            for row in conn.execute(
                    'select tran_pickle from trans ' +
                    'where lat_in = %d and lng_in = %d' % (
                        lat_in, lng_in)):
                nearby += cPickle.loads(str(row[0]))

        conn.close()
        end_time = time.time()
        _LOG.info('DB search: %.6f sec ...', end_time - start_time)

        # Apply filter / sorting
        query = Memory.Get('filter', '').encode('utf-8')
        if query:
            # User enters the criteria for sorting
            for s in nearby:
                s['AGE'] = Age(s['建築完成年月'])[:-3]  # remove 年

            rules = twrealprice_rule.Rules.Create(
                latlng=(coordinate[0], coordinate[1])
            )
            rules.ParseQuery(query)
            filters = rules.filters
            rules.CountScore(nearby)
            rules.Sort()

            Memory.Set('cached_transaction', rules.Top(MAX_CACHE_TRANS))
            return rules.Top(max_count), filters
        else:
            Memory.Set('cached_transaction', nearby[:MAX_CACHE_TRANS])
            return nearby[:max_count], []


def run(content_config, env, variables):
    """
    content_config schema:
    {
       "api_key": "xxxxx",
       "location": "location variables",
       "max_count": 3
       "distance_threshold": 0.050,
    }
    """
    msgs = []

    # output limit and map size
    size = (500, 260)
    if env['platform_type'] == SupportedPlatform.Line:
        max_count = 2
        max_text_len = 60
    else:
        max_count = content_config.get('max_count', 10)
        max_text_len = Message.MAX_TEXT_LEN

    # Check if the user requests more data. Maintain the pointers.
    more_data = Memory.Get('more_data', None)
    next_data_index = Memory.Get('next_data_index', max_count)
    cached_transaction = Memory.Get('cached_transaction', None)
    Memory.Set('more_data', '0')
    Memory.Set('next_data_index', max_count)  # could be updated soon below
    if more_data == '1' and cached_transaction:
        # Yes, user clicks 'more data', dump data from cache.

        if env['platform_type'] == SupportedPlatform.Line:
            max_count = 4

        trans = cached_transaction[next_data_index:next_data_index + max_count]
        Memory.Set('next_data_index', next_data_index + max_count)

        if not trans:
            return [Message('沒有更多物件了，請重新輸入地址或條件。')]

    else:
        # No. User enters an address or a query.
        location = Resolve(content_config['location'], variables)
        if 'coordinates' not in location:
            location = Memory.Get('location')

            if 'coordinates' not in location:
                return [Message('不正確的輸入，請重新輸入')]

        c = (location['coordinates']['lat'], location['coordinates']['long'])
        twrealprice = TwRealPrice()

        try:
            trans, filters = twrealprice.nearby_transaction(
                max_count, c, content_config['distance_threshold'])
        except IOError:
            return [Message('資料庫找不到，趕快回報給粉絲頁管理員，謝謝。')]

        if Memory.Get('filter'):
            if filters:
                msgs.append(Message('轉譯後的篩選條件: %s' % ' '.join(filters)))
            else:
                msgs.append(Message(
                    '您輸入的條件我看不懂，請試試別的條件，或是「重設條件」。'))
                return msgs

        if not trans:
            msg = Message('對不起，這裡附近沒有成交行情喔！')
            msgs.append(msg)
            return msgs

        m = GoogleStaticMapAPIRequestBuilder(content_config['api_key'], size)
        m.add_marker(c, 'purple')
        for s in trans:
            lat = float(s['latlng'][0])
            lng = float(s['latlng'][1])
            m.add_marker((lat, lng))

        subtitle = '搜尋結果僅供參考，詳細完整實價登錄資料，以內政部公佈為準。'

        # Construct main result cards.
        msg = Message()
        b = Message.Bubble('附近的成交行情',
                           image_url=m.build_url(),
                           subtitle=subtitle)

        msg.add_bubble(b)
        msgs.append(msg)

    # At this point, 'trans' must have data to show.

    for s in trans:
        try:
            def UnitPrice(s):
                try:
                    return '%.2f萬' % (
                        float(s['單價每平方公尺']) *
                        twrealprice_rule.M2_PER_PING / 10000)
                except ValueError:
                    return '--.--'

            title = ' '.join([
                '%d萬' % (int(s['總價元']) / 10000),
                '(%s * %.2f坪 + %d萬)' % (
                    UnitPrice(s),
                    float(s['建物移轉總面積平方公尺']) /
                    twrealprice_rule.M2_PER_PING,
                    int(s['車位總價元']) / 10000),
                '%s(%s)' % (
                    s['建物型態'].split('(')[0],
                    Age(s['建築完成年月']),
                ),
                '%s/共%s' % (
                    s['移轉層次'].replace('層', '樓'),
                    s['總樓層數'].replace('層', '樓')),
                StreetOnly(s),
            ]).decode('utf-8')[:max_text_len]

            subtitle = ' '.join([
                RocSlash(s['交易年月日']) + '成交',
                '%s房%s廳%s衛' % (
                    s['建物現況格局-房'],
                    s['建物現況格局-廳'],
                    s['建物現況格局-衛']),
                '地坪%.2f' % (
                    float(s['土地移轉總面積平方公尺']) /
                    twrealprice_rule.M2_PER_PING),
                '車位%.2f' % (
                    float(s['車位移轉總面積平方公尺']) /
                    twrealprice_rule.M2_PER_PING),
                s['車位類別'],
                s['主要用途'],
                '備註: ' + s['備註'] if s['備註'] else '',
            ]).decode('utf-8')[:max_text_len]

            msg = Message()
            msg.add_bubble(Message.Bubble(title, subtitle=subtitle))
            msgs.append(msg)

        except ValueError:
            traceback.print_exc()
            continue

    return msgs
