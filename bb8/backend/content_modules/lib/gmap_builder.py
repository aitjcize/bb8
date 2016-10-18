"""Provides the helper functions for static Google Maps API."""
import urllib
from bb8.backend.module_api import Config


class GoogleStaticMapAPIRequestBuilder(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/staticmap'
    REDIRECT_URL = (Config('HTTP_ROOT') +
                    '/api/third_party/youbike/render_map?url=')

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
