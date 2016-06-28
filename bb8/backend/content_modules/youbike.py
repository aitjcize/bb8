# -*- coding: utf-8 -*-
"""
    Search for Youbike Info
    ~~~~~~~~~~~~~~~~~~~~~~~

    Youbike info search according to location.

    Copyright 2016 bb8 Authors
"""

import cPickle
import gzip
import heapq
import json
import re
import tempfile
import urllib

import enum

from bb8 import config, logger
from bb8.backend.module_api import (Config, Message, LocationPayload, Resolve,
                                    SupportedPlatform)


GOOGLE_STATIC_MAP_API_KEY = 'AIzaSyBumjctKrdC-SQIITfoJakEffPIz4vR87A'


def get_module_info():
    return {
        'id': 'ai.compose.third_party.youbike',
        'name': 'Youbike',
        'description': 'Youbike info search according to location.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'youbike',
        'ui_module_name': 'youbike',
    }


def schema():
    return {
        'type': 'object',
        'required': ['send_payload_to_current_node', 'max_count', 'location',
                     'distance_threshold', 'display_weather'],
        'additionalProperties': False,
        'properties': {
            'send_payload_to_current_node': {'type': 'boolean'},
            'max_count': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 7
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
            'display_weather': {'type': 'boolean'}
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


class UbikeAPIParser(object):
    API_ENDPOINT = 'http://data.taipei/youbike'
    YOUBIKE_PHP = 'http://taipei.youbike.com.tw/cht/f11.php'

    class Direction(enum.Enum):
        In = 0
        Out = 1

    def __init__(self):
        self._data = None
        self._stations = []
        self._coordinates = {}
        self._running_sum = {}
        self._time_slot = 0.5
        self.has_average_waiting_time = True

    def refresh_data(self):
        """Refresh Youbike data.

        First try the pickle method. If it fails, fallback to the youbike PHP
        method. If it also fails, fallback to the data.taipi API.
        """
        # exception if no pickle file or len(stations_history) < 1
        try:
            self._fetch_data_pickle()
        except Exception as e:
            logger.exception(e)
            try:
                self._fetch_data_youbike_php()
            except Exception as e:
                logger.exception(e)
                self._fetch_data_taipei_data()

            self._parse_data()

    def find_knn(self, k, coordinate, threshold=0):
        """Find *k* nearest coordinate.

        If the minimum distance of the nearest coordinate is greater then
        *threshold*, return an empty list indicating that the coordinate is too
        far from all possible options.
        """
        def r_square(c1, c2):
            return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2

        h = []
        for sno in self._coordinates:
            heapq.heappush(
                h, (r_square(coordinate, self._coordinates[sno]), sno))

        knn = []
        for unused_i in range(k):
            knn.append(self._stations[heapq.heappop(h)[1]])

        min_dist = r_square((float(knn[0]['lat']), float(knn[0]['lng'])),
                            coordinate)
        if threshold and min_dist > threshold ** 2:
            return []

        return knn

    def _fetch_data_pickle(self):
        PICKLE_PATH = config.YOUBIKE_PICKLE

        with open(PICKLE_PATH, 'rb') as fh:
            (stations_history,
             self._coordinates,
             self._running_sum,
             unused_weather_parser) = cPickle.load(fh)

            # how long does the stations_history cover
            # (used to calculate average)
            self._time_slot = 30 * len(stations_history) / 60
            self._stations = stations_history[-1]

    def _fetch_data_youbike_php(self):
        data = urllib.urlopen(self.YOUBIKE_PHP).read()
        r = re.search('siteContent=\'(.*?)\'', data, re.S)
        if r:
            self._data = {'retVal': json.loads(r.group(1))}
        else:
            raise RuntimeError('can not find siteContent data')

    def _fetch_data_taipei_data(self):
        unused_fd, filename = tempfile.mkstemp()

        with open(filename, 'w') as f:
            f.write(urllib.urlopen(self.API_ENDPOINT).read())

        with gzip.open(filename, 'r') as f:
            data = f.read()

        self._data = json.loads(data)

    def _parse_data(self):
        self._stations = self._data['retVal']
        self._coordinates = dict(
            (str(x['sno']), (float(x['lat']), float(x['lng'])))
            for x in self._stations.values())
        self._running_sum = dict((k, (0, 0)) for k in self._stations)
        self.has_average_waiting_time = False

    def data(self):
        return (self._stations,
                self._coordinates,
                dict((k, (0, 0)) for k in self._stations))

    def average_waiting_time(self, sno, direction):
        return (self._time_slot /
                max(self._running_sum[sno][direction.value], 1))


def run(content_config, env, variables):
    """
    content_config schema:
    {
       "send_payload_to_current_node": true,
       "location": "location variables",
       "max_count": 3
       "distance_threshold": 0.050,
       "display_weather": true
    }
    """

    location = Resolve(content_config['location'], variables)
    if 'coordinates' not in location:
        return [Message('不正確的輸入，請重新輸入')]

    c = (location['coordinates']['lat'], location['coordinates']['long'])
    youbike = UbikeAPIParser()
    youbike.refresh_data()

    k = content_config.get('max_count', 5)
    size = (500, 260)

    if env['platform_type'] == SupportedPlatform.Line:
        k = 2
        size = (1000, 1000)

    stations = youbike.find_knn(k, c, content_config['distance_threshold'])
    if not stations:
        return [Message('對不起，這裡附近沒有 Ubike 站喔！')]

    m = GoogleStaticMapAPIRequestBuilder(GOOGLE_STATIC_MAP_API_KEY, size)
    m.add_marker(c, 'purple')
    for s in stations:
        m.add_marker((float(s['lat']), float(s['lng'])))

    msgs = []

    # Construct main result cards.
    msg = Message()
    b = Message.Bubble(u'附近的 Ubike 站點',
                       image_url=m.build_url(),
                       subtitle=u'以下是最近的 %d 個站點' % k)

    best = stations[0]
    for s in stations:
        if s['sbi'] > 0:
            best = s
            break

    best_gps_coord = (float(best['lat']), float(best['lng']))
    b.add_button(Message.Button(Message.ButtonType.WEB_URL, u'帶我去',
                                url=m.build_navigation_url(best_gps_coord)))

    to_current = content_config['send_payload_to_current_node']

    # Only facebook have postback button for now
    if env['platform_type'] == SupportedPlatform.Facebook:
        b.add_button(Message.Button(Message.ButtonType.POSTBACK, u'再次查詢',
                                    payload=LocationPayload(c, to_current)))
    msg.add_bubble(b)

    for s in stations:
        m.clear_markers()
        m.add_marker(c, 'purple')

        gps_coord = (float(s['lat']), float(s['lng']))
        m.add_marker(gps_coord, color='red')

        sbi, bemp = int(s['sbi']), int(s['bemp'])
        subtitle = u'剩餘數量: %d\n空位數量: %d\n' % (sbi, bemp)

        if youbike.has_average_waiting_time:
            if sbi < 5:
                subtitle += (u'預計進車時間: %d 分鐘\n' %
                             youbike.average_waiting_time(
                                 str(s['sno']), youbike.Direction.In))
            if bemp < 5:
                subtitle += (u'預計出位時間：%d 分鐘\n' %
                             youbike.average_waiting_time(
                                 str(s['sno']), youbike.Direction.Out))

        b = Message.Bubble(s['ar'], image_url=m.build_url(), subtitle=subtitle)
        b.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    u'地圖導航',
                                    url=m.build_navigation_url(gps_coord)))
        msg.add_bubble(b)

    msgs.append(msg)

    if content_config['display_weather'] and 'weather' in best:
        weather = best['weather']
        code = best['weather']['weather_code']
        temp = weather['temp']

        if code / 100 == 3 or code in [500, 520]:
            msgs.append(Message(u'提醒您，現在外面天雨路滑，騎車小心！'
                                u'記得帶傘或穿件雨衣唷'))
        elif (code / 100 == 2 or
              code in [501, 502, 503, 504, 511, 521, 522, 531, 901, 902]):
            msgs.append(Message(u'現在外面大雨滂沱，不如叫個 Uber 吧！'))
        elif code in [904] or temp >= 30:
            msgs.append(Message(u'提醒您，現在外面天氣炎熱(攝氏%.1f度)，'
                                u'記得做好防曬唷' % temp))

    return msgs
