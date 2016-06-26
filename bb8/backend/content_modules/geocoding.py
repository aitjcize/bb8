# -*- coding: utf-8 -*-
"""
    Geocoding
    ~~~~~~~~~

    Given input query address, display possible result as button selections.
    Each button embedes the gps location of the location, which delivers a
    location input when pressed.

    Copyright 2016 bb8 Authors
"""

import requests

from bb8.backend.module_api import (LocationPayload, Message, Resolve,
                                    SupportedPlatform, TextPayload)


def get_module_info():
    return {
        'id': 'ai.compose.core.geocoding',
        'name': 'Geocoding',
        'description': 'Convert an address to a list of possible GPS '
                       'locations which users can select from.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'geocoding',
        'ui_module_name': 'geocoding',
    }


def schema():
    return {
        'type': 'object',
        'required': ['parse_payload_in_current_node', 'api_key', 'query_term',
                     'language', 'region', 'bounds'],
        'additionalProperties': True,
        'properties': {
            'parse_payload_in_current_node': {'type': 'boolean'},
            'api_key': {'type': 'string'},
            'query_term': {'type': 'string'},
            'language': {'type': 'string'},
            'region': {'type': 'string'},
            'bounds': {
                'type': 'array',
                'items': {'$ref': '#/definitions/gps'},
                'minItems': 2,
                'maxItems': 2
            },
            'center': {'$ref': '#/definitions/gps'}
        },
        'definitions': {
            'gps': {
                'type': 'object',
                'required': ['lat', 'long'],
                'additionalProperties': False,
                'properties': {
                    'lat': {'type': 'number'},
                    'long': {'type': 'number'}
                }
            }
        }
    }


class GoogleMapsGeocodingAPI(object):
    API_ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'

    def __init__(self, api_key):
        self._api_key = api_key

    def query_top_n(self, n, address, language, region, bounds, center=None):
        params = {
            'key': self._api_key,
            'address': address,
            'language': language,
            'region': region,
            'bounds': '%f,%f|%f,%f' % (bounds[0] + bounds[1])
        }
        response = requests.request(
            'GET',
            self.API_ENDPOINT,
            params=params)

        if response.status_code != 200:
            raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                                response.text))
        result = response.json()['results']

        # Remove result if it's outside of bounding box
        filtered_result = []
        for r in result:
            coordinate = r['geometry']['location'].values()
            if (coordinate[0] <= bounds[0][0] and
                    coordinate[0] >= bounds[1][0] and
                    coordinate[1] >= bounds[0][1] and
                    coordinate[1] <= bounds[1][1]):
                filtered_result.append(r)

        # Sort result according to distance to center
        if center:
            def r_square(lt):
                ct = lt['geometry']['location'].values()
                cc = center.values()
                return (ct[0] - cc[0]) ** 2 + (ct[1] - cc[1]) ** 2
            filtered_result = sorted(filtered_result, key=r_square)

        final_result = []
        for i in range(min(n, len(filtered_result))):
            location = filtered_result[i]['geometry']['location']
            final_result.append({
                'address': filtered_result[i]['formatted_address'],
                'location': (location['lat'], location['lng'])
            })

        return final_result


def run(content_config, unused_env, variables):
    """
    content_config schema:

    Platform dependent message:
    {
        'parse_payload_in_current_node': False,
        'api_key': 'google geocoding api key',
        'query_term': 'query term',
        'language': 'zh_TW',
        'region': 'tw',
        'bounds': [
            {'lat': 25.314444, 'long': 119.781068},
            {'lat': 23.816576, 'long': 122.053702}
        ],
        'center': {'lat': 23.816576, 'long': 122.053702}
    }
    """
    query_term = Resolve(content_config['query_term'], variables)
    cfg = content_config

    api = GoogleMapsGeocodingAPI(content_config['api_key'])

    b = cfg['bounds']
    bounds = [(b[0]['lat'], b[0]['long']), (b[1]['lat'], b[1]['long'])]

    results = api.query_top_n(3, query_term, cfg['language'],
                              cfg['region'], bounds, cfg['center'])

    in_currrent = content_config['parse_payload_in_current_node']

    m = Message()
    if not results:
        m.text = '對不起，我找不到這個地址, 請重新輸入 >_<'
    elif len(results) == 1:
        m.set_buttons_text('你指的是「%s」嗎？' %
                           results[0]['address'].encode('utf8'))
        m.add_button(
            Message.Button(Message.ButtonType.POSTBACK, '是',
                           payload=LocationPayload(results[0]['location'],
                                                   in_currrent)))
        m.add_button(
            Message.Button(Message.ButtonType.POSTBACK, '否',
                           payload=TextPayload('WRONG_ADDRESS', in_currrent)))
    else:
        m.set_buttons_text('你指的是以下哪一個地址呢?')
        for r in results:
            m.add_button(Message.Button(Message.ButtonType.POSTBACK,
                                        r['address'],
                                        payload=LocationPayload(r['location'],
                                                                in_currrent)))

    return [m]
