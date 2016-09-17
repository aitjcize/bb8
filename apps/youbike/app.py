#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Youbike Data Collection Daemon
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Colllect youbike and weather data in the background and store it as a
    pickle file, which is later used by the bb8 youbike content module.

    Copyright 2016 bb8 Authors
"""

import argparse
import cPickle
import gzip
import heapq
import itertools
import json
import logging
import os
import re
import sys
import tempfile
import time
import urllib

from datetime import datetime, timedelta

import enum
import grpc

from concurrent import futures

import service_pb2  # pylint: disable=E0401


_GRPC_MAX_WORKERS = 10


class WeatherAPIParser(object):
    CITY_IDS = [7280291, 1668841, 1668467, 1670029, 1668664, 1668338, 1668341,
                1675720, 1673169, 6724653, 1668399, 1672430, 6748079, 1668885,
                1669321, 1665148, 6749202, 6748075, 1669401, 6643057, 1678813,
                1676087, 1673046, 7280288, 1668630, 1677028, 1676453, 1670395,
                6600589, 1675107, 1675151, 6696918, 7601921, 1667031, 1667289,
                1667905, 1668396, 1677112, 1679136, 7552914, 6749251, 1665988]

    REFRESH_TIMEOUT = 60 * 10

    API_ENDPOINT = ('http://api.openweathermap.org/data/2.5/'
                    'weather?id=%d&APPID=735665d5fc6167c6f2d5a33e803d1d50')

    def __init__(self, serialized_data=None):
        self._last_refresh = datetime(1970, 1, 1)
        if not isinstance(serialized_data, tuple):
            self.refresh()
            return

        self._weather, self._last_refresh = serialized_data

    def refresh(self):
        if (datetime.now() - self._last_refresh <
                timedelta(seconds=self.REFRESH_TIMEOUT)):
            return

        logging.info('Updating weather database ...')
        self._weather = []
        for city in self.CITY_IDS:
            try:
                data = json.load(urllib.urlopen(self.API_ENDPOINT % city))
                lon, lat = data['coord']['lon'], data['coord']['lat']
                temperature = data['main']['temp']
                humidity = data['main']['humidity']
                weather_code = data['weather'][0]['id']
                temperature = temperature - 273.15
                self._weather.append(dict(lon=lon, lat=lat,
                                          temp=temperature,
                                          humidity=humidity,
                                          weather_code=weather_code))
            except Exception:
                logging.warning('Cannot fetch city: %d', city)
                continue

        self._last_refresh = datetime.now()
        logging.info('Weather database completed.')

    def query(self, lon, lat):
        """Given longtitude and latitude, find the closest point that has
        weather info.

        We don't have many data point so a linear search should be good enough.
        """
        def distance(lon1, lat1, lon2, lat2):
            return (lon2 - lon1) ** 2 + (lat2 - lat1) ** 2

        min_distance = sys.maxint
        weather = {}
        for w in self._weather:
            d = distance(lon, lat, w['lon'], w['lat'])
            if d < min_distance:
                min_distance = d
                weather = w

        return dict(temp=weather['temp'],
                    humidity=weather['humidity'],
                    weather_code=weather['weather_code'])

    def serialize(self):
        return (self._weather, self._last_refresh)


class YoubikeAPI(object):
    API_ENDPOINT = 'http://data.taipei/youbike'
    YOUBIKE_PHP = 'http://taipei.youbike.com.tw/cht/f11.php'

    def __init__(self):
        self._data = None
        self.stations = {}
        self.coordinates = {}

    def refresh_data(self):
        self._fetch_data()
        self._parse_data()

    def _fetch_data(self):
        self._fetch_data_youbike_php()

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
        self.stations = self._data['retVal']
        self.coordinates = dict(
            (str(x['sno']), (float(x['lat']), float(x['lng'])))
            for x in self.stations.values())


class YoubikeDataCollector(object):
    """YoubikeDataCollector provides a running average of ubike data"""

    class Direction(enum.Enum):
        In = 0
        Out = 1

    def __init__(self, pickle_path='', interval=30):
        """constructor.

        Args:
            pickle_path: The path to store pickle file
            interval: The interval to fetch the ubike data
        """
        if pickle_path == '':
            raise RuntimeError('Please provide the path to store pickled data')

        self._pickle_path = pickle_path
        self._history_size = 3600 / interval
        self._time_slot = float(interval) / 60

        try:
            with open(pickle_path, 'rb') as fh:
                (self._stations_history,
                 self._coordinates,
                 self._running_sum,
                 self._weather_parser) = cPickle.load(fh)

            self._time_slot = interval * len(self._stations_history) / 60
            self._stations = self._stations_history[-1]
        except Exception:
            self._stations_history = []
            self._coordinates = {}
            self._running_sum = {}
            self._stations = []
            self._weather_parser = None
        self._weather_parser = WeatherAPIParser(self._weather_parser)

    def refresh(self, stations, coordinates):
        self._stations = stations
        self._coordinates = coordinates
        self._weather_parser.refresh()

        def pairwise(iterable):
            "s -> (s0, s1), (s1, s2), (s2, s3), ..."
            a, b = itertools.tee(iterable)
            next(b, None)
            return zip(a, b)

        for k in stations:
            stations[k]['weather'] = self._weather_parser.query(
                float(stations[k]['lng']), float(stations[k]['lat']))

        if self._coordinates != coordinates:
            self._coordinates = coordinates

        # remove the unnecessary content to reduce pickle size
        self._stations_history = [
            dict((k, dict(sbi=s[k]['sbi'], bemp=s[k]['bemp'])) for k in s)
            for s in self._stations_history]
        self._stations_history.append(stations)

        if len(self._stations_history) >= self._history_size:
            drop_size = len(self._stations_history)-self._history_size
            self._stations_history = self._stations_history[drop_size:]

        for k in coordinates:
            # diff_list is the pairwise difference
            # (if difference is negative, use 0) of the sbi, bemp in stations
            # example: sbi, bemp in stations is:
            # [{sbi: 1, bemp: 2}, {sbi: 5, bemp: 5}, {sbi: 3, bemp: 2}]
            # diff_list is: [(4, 3), (0, 3)]
            diff_list = [(max(int(y.get(k, {}).get('sbi', 0)) -
                              int(x.get(k, {}).get('sbi', 0)), 0),
                          max(int(y.get(k, {}).get('bemp', 0)) -
                              int(x.get(k, {}).get('bemp', 0)), 0))
                         for x, y in pairwise(self._stations_history)]

            self._running_sum[k] = (sum(d[0] for d in diff_list),
                                    sum(d[1] for d in diff_list))

    def serialize(self):
        """Serialize the context into a file."""
        # Employ RCU method to prevent race condition.
        update_pickle = self._pickle_path + '.tmp'
        with open(update_pickle, 'wb') as fh:
            cPickle.dump((self._stations_history,
                          self._coordinates,
                          self._running_sum,
                          self._weather_parser.serialize()), fh)

        os.rename(update_pickle, self._pickle_path)

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

    def average_waiting_time(self, sno, direction):
        return int(self._time_slot /
                   max(self._running_sum[sno][direction.value], 1))


class YoubikeInfoServicer(service_pb2.YoubikeInfoServicer):
    def __init__(self, _collector):
        self._collector = _collector
        super(YoubikeInfoServicer, self).__init__()

    def FindKnn(self, request, unused_context):
        return service_pb2.FindKnnReply(object=cPickle.dumps(
            self._collector.find_knn(
                request.k,
                (request.lat, request.long),
                request.threshold)))

    def GetAverageWaitingTime(self, request, unused_context):
        direction = (YoubikeDataCollector.Direction.In
                     if request.direction == 0 else
                     YoubikeDataCollector.Direction.Out)
        return service_pb2.GetAverageWaitingTimeReply(
            minutes=self._collector.average_waiting_time(
                request.sno, direction))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Youbike data collection '
                                                 'daemon')
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        action='store_true', default=False,
                        help='Run in the background.')
    parser.add_argument('-p', '--port', dest='port', default=9999,
                        help='gRPC service port')
    parser.add_argument('--pickle_path',
                        dest='pickle_path',
                        default='/var/lib/youbike/youbike.pickle',
                        help='The path of pickled file to store the data')
    parser.add_argument('--interval',
                        type=int,
                        dest='interval',
                        default=30,
                        help='The interval to fetch youbike data (second)')
    args = parser.parse_args()

    # Setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(message)s', '%Y/%m/%d %H:%M:%S')
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if args.daemonize:
        pid = os.fork()
        if pid != 0:
            logging.info('Forked into background (pid=%d)', pid)
            sys.exit(1)

    ubike_api = YoubikeAPI()
    collector = YoubikeDataCollector(pickle_path=args.pickle_path,
                                     interval=args.interval)

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=_GRPC_MAX_WORKERS))
    service_pb2.add_YoubikeInfoServicer_to_server(
        YoubikeInfoServicer(collector), server)
    server.add_insecure_port('[::]:%d' % args.port)
    server.start()

    while True:
        try:
            ubike_api.refresh_data()
        except Exception as e:
            logging.exception('Youbike data refresh failed, skipping')
            continue

        collector.refresh(ubike_api.stations, ubike_api.coordinates)
        collector.serialize()
        time.sleep(args.interval)
