import argparse
import gzip
import json
import re
import tempfile
import urllib
import pickle
import itertools
import logging
import sys
import time
from datetime import datetime, timedelta


class UbikeDataCollector(object):
    """UbikeDataCollector provides a running average of ubike data"""
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

        try:
            with open(pickle_path, 'rb') as fh:
                (self._stations_history,
                 self._coordinates,
                 self._running_sum,
                 self._weather_parser) = pickle.load(fh)
        except Exception:
            self._stations_history = []
            self._coordinates = {}
            self._running_sum = {}
            self._weather_parser = None
        self._weather_parser = WeatherAPIParser(self._weather_parser)

    def refresh(self, stations, coordinates):
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
        with open(self._pickle_path, 'wb') as fh:
            pickle.dump((self._stations_history,
                         self._coordinates,
                         self._running_sum,
                         self._weather_parser.serialize()), fh)


class UbikeAPIParser(object):
    API_ENDPOINT = 'http://data.taipei/youbike'
    YOUBIKE_PHP = 'http://taipei.youbike.com.tw/cht/f11.php'

    def __init__(self):
        self._data = None
        self.stations = []
        self.coordinates = {}

    def refresh_data(self):
        self._fetch_data_youbike_php()
        self._parse_data()

    def _fetch_data_youbike_php(self):
        data = urllib.urlopen(self.YOUBIKE_PHP).read()
        r = re.search('siteContent=\'(.*?)\'', data, re.S)
        if r:
            self._data = {'retVal': json.loads(r.group(1))}
        else:
            self._fetch_data_taipei_data()

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


class WeatherAPIParser(object):
    CITY_IDS = [7280291, 1668841, 1668467, 1670029, 1668664, 1668338, 1668341,
                1675720, 1673169, 6724653, 1668399, 1672430, 6748079, 1668885,
                1669321, 7280290, 1665148, 6749202, 6748075, 1669401, 6643057,
                1678813, 1676087, 1673046, 7280288, 1668630, 1677028, 1676453,
                1670395, 6600589, 1675107, 1675151, 6696918, 7601921, 1667031,
                1667289, 1667905, 1668396, 1677112, 1679136, 7552914, 6749251,
                1665988]

    REFRESH_TIMEOUT = 60 * 10

    API_ENDPOINT = 'http://api.openweathermap.org/data/2.5/' \
                   'weather?id=%d&APPID=735665d5fc6167c6f2d5a33e803d1d50'

    def __init__(self, serialized_data=None):
        if not isinstance(serialized_data, tuple):
            self._refresh()
            return
        self._weather, self._last_refresh = serialized_data
        if datetime.now() - self._last_refresh > \
           timedelta(seconds=self.REFRESH_TIMEOUT):
            self._refresh()

    def _refresh(self):
        self._weather = []
        for city in self.CITY_IDS:
            data = json.loads(urllib.urlopen(self.API_ENDPOINT % city).read())
            lon, lat = data['coord']['lon'], data['coord']['lat']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            weather_code = data['weather'][0]['id']
            temperature = temperature - 273.15
            self._weather.append(dict(lon=lon, lat=lat,
                                      temp=temperature,
                                      humidity=humidity,
                                      weather_code=weather_code))
        logging.warning('end fetching weather information')
        self._last_refresh = datetime.now()

    # TODO(yunchiao.li): query will probably be a performance bottleneck
    def query(self, lon, lat):
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


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='')
    cli_parser.add_argument('--pickle_path',
                            dest='pickle_path',
                            default='',
                            help='The path of pickled file to store the data')
    cli_parser.add_argument('--interval',
                            type=int,
                            dest='interval',
                            default=30,
                            help='The interval to fetch youbike data (second)')
    args = cli_parser.parse_args()

    while True:
        ubike_parser = UbikeAPIParser()
        ubike_parser.refresh_data()

        collector = UbikeDataCollector(pickle_path=args.pickle_path,
                                       interval=args.interval)
        collector.refresh(ubike_parser.stations, ubike_parser.coordinates)
        collector.serialize()

        time.sleep(args.interval)
