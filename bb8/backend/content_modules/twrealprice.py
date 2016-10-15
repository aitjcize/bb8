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

from bb8.backend.module_api import (Config, Message, Memory,
                                    SupportedPlatform, LocationPayload)
from bb8.backend.content_modules.geocoding import GoogleMapsGeocodingAPI
import twrealprice_rule


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


GOOGLE_STATIC_MAP_API_KEY = 'AIzaSyCpP0pV9_YtQuV-Gzf6aL9nRt1Es5UlBv4'

# Maximum number of transaction to cache for "more data" feature.
MAX_CACHE_TRANS = 50  # 50 / 5 = 10 pages

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


def MarkerStyle():
    yield 'color:purple'
    i = -1
    while True:
        i += 1
        yield 'color:red|label:%c' % (i + ord('A'))


def Deser(obj):
    """Helper function for de-serialization.

    Args:
      obj: None or pickled str.

    Returns:
      None or the object.
    """
    if obj:
        return cPickle.loads(obj)
    return None


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
        'properties': {
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

    def add_marker(self, coordinate, style):
        self._markers[coordinate] = style

    def remove_marker(self, coordinate):
        del self._markers[coordinate]

    def clear_markers(self):
        self._markers = {}

    def _markers_string(self):
        return '&'.join(['markers=%s|%3.8f,%3.8f' %
                         ((style,) + coordinate)
                         for coordinate, style in self._markers.iteritems()])

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

    def nearby_transaction(self, max_count, latlng, rules):
        """Returns transaction data near 'latlng' sorted by 'rules'.

        Args:
          max_count: int.
          latlng: tuple.
          rules: Rules. None: no criteria entered so far.

        Returns:
          list of transaction data.
        """

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
            lat_center, lng_center = LatLngIndex(latlng[0], latlng[1])
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

        for s in nearby:
            s['AGE'] = Age(s['建築完成年月'])[:-3]  # remove 年

        if not rules:
            rules = twrealprice_rule.Rules()
            rules.AddPureSortingRules(latlng)
        rules.CountScore(nearby)
        rules.Sort()

        Memory.Set('cached_transaction', rules.Top(MAX_CACHE_TRANS))
        return rules.Top(max_count)


class UserInput(object):
    KEYS = ['reset', 'more_data', 'location', 'query']

    def __init__(self):
        # First time, read from bot and clear them.
        self.singleton = {k: Memory.Get(k, None) for k in self.KEYS}
        # Query is special because it is Unicode.
        if self.singleton['query']:
            self.singleton['query'] = self.singleton['query'].encode('utf-8')
        _LOG.info('User input: %r', self.singleton)

        for k in self.KEYS:
            Memory.Set(k, None)

    def Get(self, key):
        return self.singleton[key]


def run(unused_content_config, env, unused_variables):
    user_input = UserInput()
    msgs = []  # The output messages.

    # output limit and map size
    size = (500, 260)
    if env['platform_type'] == SupportedPlatform.Line:
        max_count = 2
        max_text_len = 60
    else:
        max_count = 5
        max_text_len = Message.MAX_TEXT_LEN

    address = ''   # str. The address user entered.

    geocoder = GoogleMapsGeocodingAPI(api_key=GOOGLE_STATIC_MAP_API_KEY)

    more_data = user_input.Get('more_data')
    latlng = Memory.Get('latlng', None)  # tuple. User's current location.
    cached_transaction = Memory.Get('cached_transaction', None)
    next_data_index = Memory.Get('next_data_index', max_count)
    if more_data:
        # Yes, user clicks 'more data', dump data from cache.

        if not cached_transaction:
            return [Message('請重新輸入地址或條件。')]

        trans = cached_transaction[next_data_index:next_data_index + max_count]
        Memory.Set('next_data_index', next_data_index + max_count)

        if not trans:
            return [Message('沒有更多物件了，請重新輸入地址或條件。')]

    else:
        # Nope. User is not entering 'more data'.

        reset = user_input.Get('reset')
        location = user_input.Get('location')

        if reset:
            latlng = Memory.Get('latlng', None)
            rules = None

        # User uploaded current location.
        elif location and 'coordinates' in location:
            latlng = (
                location['coordinates']['lat'],
                location['coordinates']['long'])

            rules = Deser(Memory.Get('rules', None))

        else:  # User entered either an address or criteria; or both.
            query = user_input.Get('query')
            rules = twrealprice_rule.Rules.Create()
            query = rules.ParseQuery(query)

            address = query.strip()
            _LOG.info(
                'User query: address=[%s] filters:[%s]',
                address, rules.filters)
            if address:
                if latlng:
                    center = {'lat': latlng[0], 'long': latlng[1]}
                else:
                    center = None

                geo_results = geocoder.query_top_n(
                    n=3,
                    address=address,
                    language='zh_TW',
                    region='TW',
                    bounds=[[
                        [20.0, 118.0],
                        [26.0, 123.0]]],
                    center=center)

                if not geo_results and not rules.filters:
                    return [Message('我不認識這個地址: [%s]' % address)]

                if len(geo_results) == 1:
                    latlng = (geo_results[0]['location'][0],
                              geo_results[0]['location'][1])

                if len(geo_results) > 1:
                    m = Message(buttons_text=u'你指的是以下哪一個地址呢?')
                    for r in geo_results:
                        m.add_button(Message.Button(
                            Message.ButtonType.POSTBACK,
                            r['address'],
                            payload=LocationPayload(
                                r['location'],
                                False)))

                    # If user also entered criteria, save it for later query.
                    if rules.filters:
                        Memory.Set('rules', cPickle.dumps(rules))

                    return [m]

            if not rules.filters:
                # If user didn't enter filter, use the previous one.
                rules = Deser(Memory.Get('rules', None))
                if rules:
                    _LOG.info('User prev rules: %s', rules.filters)
            if rules:
                rules.AddPureSortingRules(latlng)

        if not latlng:
            return [Message(
                '我還不知道你想查的地方是哪裡。請輸入地址或是送出你的位置。')]

        Memory.Set('rules', cPickle.dumps(rules))
        Memory.Set('latlng', latlng)

        twrealprice = TwRealPrice()
        try:
            trans = twrealprice.nearby_transaction(max_count, latlng, rules)
        except IOError:
            return [Message('資料庫找不到，趕快回報給粉絲頁管理員，謝謝。')]

        if rules and rules.filters:
            msgs.append(Message('篩選條件: %s' % ' '.join(rules.filters)))

        if not trans:
            msg = Message('對不起，找不到成交行情喔！試試別的地址或條件。')
            msgs.append(msg)
            return msgs

    # Construct main result cards.
    main_map = GoogleStaticMapAPIRequestBuilder(
        GOOGLE_STATIC_MAP_API_KEY, size)
    style = MarkerStyle()
    main_map.add_marker(latlng, style.next())
    for s in trans:
        lat = float(s['latlng'][0])
        lng = float(s['latlng'][1])
        main_map.add_marker((lat, lng), style.next())

    subtitle = '搜尋結果僅供參考，詳細完整實價登錄資料，以內政部公佈為準。'

    msg = Message()
    b = Message.Bubble('%s附近的成交行情' % address,
                       image_url=main_map.build_url(),
                       subtitle=subtitle)

    msg.add_bubble(b)
    msgs.append(msg)

    # At this point, 'trans' must have data to show.

    i = -1
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

            i += 1

            msg = Message()
            msg.add_bubble(Message.Bubble(
                ('%c: ' % (i + ord('A'))) + title,
                subtitle=subtitle))
            msgs.append(msg)

        except ValueError:
            traceback.print_exc()
            continue

    return msgs
