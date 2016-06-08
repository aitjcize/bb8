# -*- coding: utf-8 -*-
"""
    Search for Youbike Info
    ~~~~~~~~~~~~~~~~~~~~~~~

    Youbike info search according to location.

    Copyright 2016 bb8 Authors
"""

import gzip
import heapq
import json
import tempfile
import urllib

from bb8.backend.module_api import Message, Resolve


GOOGLE_STATIC_MAP_API_KEY = 'AIzaSyBumjctKrdC-SQIITfoJakEffPIz4vR87A'


def get_module_info():
    return {
        'id': 'ai.compose.third_party.youbike',
        'name': 'Youbike',
        'description': 'Youbike info search according to location.',
        'module_name': 'youbike',
        'ui_module_name': 'youbike',
    }


class GoogleStaticMapAPIRequestBuilder(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/staticmap'

    def __init__(self, api_key, size):
        self._api_key = api_key
        self._size = '%dx%d' % size
        self._maptype = 'roadmap'
        self._markers = []

    def add_marker(self, coordinate):
        self._markers.append('%3.8f,%3.8f' % coordinate)

    def clear_markers(self):
        self._markers = []

    def build_url(self):
        return ('%s?key=%s&size=%s&maptype=%s&markers=color:red|%s' %
                (self.API_ENDPOINT, self._api_key, self._size, self._maptype,
                 '|'.join(self._markers)))

    @classmethod
    def build_navigation_url(cls, c):
        return 'http://maps.google.com/?daddr=%3.8f,%3.8f' % c


class UbikeAPIParser(object):
    API_ENDPOINT = 'http://data.taipei/youbike'

    def __init__(self):
        self._data = None
        self._ids = []
        self._stations = []
        self._coordinates = {}

    def refresh_data(self):
        self._fetch_data()
        self._parse_data()

    def find_knn(self, k, coordinate):
        def r_square(c1, c2):
            return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2

        h = []
        for sno in self._coordinates:
            heapq.heappush(
                h, (r_square(coordinate, self._coordinates[sno]), sno))

        knn = []
        for unused_i in range(k):
            knn.append(self._stations[heapq.heappop(h)[1]])

        return knn

    def _fetch_data(self):
        unused_fd, filename = tempfile.mkstemp()

        with open(filename, 'w') as f:
            f.write(urllib.urlopen(self.API_ENDPOINT).read())

        with gzip.open(filename, 'r') as f:
            data = f.read()

        self._data = json.loads(data)

    def _parse_data(self):
        self._ids = self._data['retVal'].keys()
        self._stations = self._data['retVal']

        self._coordinates = dict((x['sno'], (float(x['lat']), float(x['lng'])))
                                 for x in self._stations.values())


def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
       "location": "location variables",
       "max_count": 3
    }
    """
    location = Resolve(content_config['location'], variables)
    if 'coordinates' not in location:
        return [Message('This is not a valid location!')]

    c = (location['coordinates']['lat'], location['coordinates']['long'])
    youbike = UbikeAPIParser()
    youbike.refresh_data()

    k = content_config.get('max_count', 3)
    stations = youbike.find_knn(k, c)

    m = GoogleStaticMapAPIRequestBuilder(GOOGLE_STATIC_MAP_API_KEY, (600, 300))
    for s in stations:
        m.add_marker((float(s['lat']), float(s['lng'])))

    msg = Message()
    msg.add_bubble(Message.Bubble(u'附近的 Ubike 站點',
                                  image_url=m.build_url(),
                                  subtitle=u'以下是最近的 %d 個站點' % k))

    for s in stations:
        m.clear_markers()
        gps_coord = (float(s['lat']), float(s['lng']))
        m.add_marker(gps_coord)
        b = Message.Bubble(s['ar'], image_url=m.build_url(),
                           subtitle=u'剩餘車數量: %s\n空位數量: %s\n' %
                           (s['sbi'], s['bemp']))
        b.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    u'地圖導航',
                                    url=m.build_navigation_url(gps_coord)))

        msg.add_bubble(b)

    return [msg]
