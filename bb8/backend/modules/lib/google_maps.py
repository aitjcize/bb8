# -*- coding: utf-8 -*-
"""
    GoogleMaps
    ~~~~~~~~~~

    GoogleMaps related helper functions.

    Copyright 2016 bb8 Authors
"""

import urllib
import requests
from bb8.backend.module_api import Config


class GoogleMapsPlaceAPI(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

    def __init__(self, api_key):
        self._api_key = api_key

    def build_address(self, item):
        name = item.get('name', '')
        address = item.get('formatted_address', '')

        if name in address:
            return address
        else:
            return ' '.join([name, address])

    def query_top_n(self, n, address, language, region, bounds, center=None):
        """Query top *n* possible location that matches *address*.

        Args:
          n: int. number of max return values
          address: str. the address to query
          language: str. the locale code (i.e. zh_TW). None for not specified.
          region: str. the country code (i.e. TW). None for not specified.
          bounds: array of [(lower_lat, lower_lng), (upper_lat, upper_lng)].
                  Empty for not specified.
          center: dict. {'lat': float, 'long': float}. None for not specified.
        """

        # Calculate the max bounding box that cover all bounds
        if bounds:
            lats = reduce(lambda x, y: x + y,
                          [[b[0][0], b[1][0]] for b in bounds], [])
            longs = reduce(lambda x, y: x + y,
                           [[b[0][1], b[1][1]] for b in bounds], [])

            max_bounds = [(min(lats), min(longs)), (max(lats), max(longs))]
        else:
            bounds = [[[-999, -999], [999, 999]]]
            max_bounds = None

        params = {
            'key': self._api_key,
            'query': address,
        }
        if language:
            params['language'] = language
        if region:
            params['region'] = region
        if max_bounds:
            params['bounds'] = '%f,%f|%f,%f' % (max_bounds[0] + max_bounds[1])
        response = requests.request(
            'GET',
            self.API_ENDPOINT,
            params=params)
        response.raise_for_status()

        result = response.json()['results']

        # Remove result if it's outside of bounding box
        filtered_result = []
        for r in result:
            coordinate = r['geometry']['location'].values()
            for b in bounds:
                if (coordinate[0] >= b[0][0] and
                        coordinate[0] <= b[1][0] and
                        coordinate[1] >= b[0][1] and
                        coordinate[1] <= b[1][1]):
                    filtered_result.append(r)

        # Sort result according to distance to center
        if center:
            def r_square(lt):
                ct = lt['geometry']['location'].values()
                cc = center.values()
                return (ct[0] - cc[0]) ** 2 + (ct[1] - cc[1]) ** 2
            filtered_result = sorted(filtered_result, key=r_square)

        final_result = []
        addrs = set()
        for i in range(min(n, len(filtered_result))):
            address = self.build_address(filtered_result[i])
            if address in addrs:
                continue
            addrs.add(address)
            location = filtered_result[i]['geometry']['location']
            final_result.append({
                'address': address,
                'location': (location['lat'], location['lng'])
            })

        return final_result


class GoogleMapsGeocodingAPI(object):
    """Google Maps Geocoding API

    Only reverse geocoding is implemented for now.
    """
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'

    def __init__(self, api_key):
        self._api_key = api_key

    def reverse(self, latlng, language, result_types=None):
        result_types = result_types or []

        params = {
            'key': self._api_key,
            'latlng': '%s,%s' % latlng,
            'language': language,
            'result_type': '|'.join(result_types)
        }
        response = requests.request(
            'GET',
            self.API_ENDPOINT,
            params=params)
        response.raise_for_status()
        results = response.json()['results']

        if results:
            return results[0]['formatted_address']


class GoogleStaticMapAPIRequestBuilder(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/staticmap'
    REDIRECT_URL = (Config('HTTP_ROOT') +
                    'api/third_party/youbike/render_map?url=')

    def __init__(self, api_key, size):
        self._api_key = api_key
        self._size = '%dx%d' % size
        self._maptype = 'roadmap'
        self._markers = {}

    def add_marker(self, coordinate, color=None, label=None):
        styles = []
        if color:
            styles.append('color:%s' % color)
        if label:
            styles.append('label:%s' % label)
        self._markers[coordinate] = '|'.join(styles)

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
