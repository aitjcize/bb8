# -*- coding: utf-8 -*-
"""
    Geocoding
    ~~~~~~~~~

    Given input query address, display possible result as button selections.
    Each button embedes the gps location of the location, which delivers a
    location input when pressed.

    Copyright 2016 bb8 Authors
"""

import re

from bb8.backend.module_api import (EventPayload, Message,
                                    Resolve, SupportedPlatform,
                                    LocationPayload, ModuleTypeEnum,
                                    PureContentModule)
from bb8.backend.modules.lib.google_maps import GoogleMapsPlaceAPI


STOP_WORDS = u'(我|在|要|去|的|到)'


def properties():
    return {
        'id': 'ai.compose.content.core.geocoding',
        'type': ModuleTypeEnum.Content,
        'name': 'Geocoding',
        'description': 'Convert an address to a list of possible GPS '
                       'locations which users can select from.',
        'supported_platform': SupportedPlatform.All,
        'variables': []
    }


def schema():
    return {
        'type': 'object',
        'required': ['send_payload_to_current_node', 'api_key', 'query_term',
                     'language', 'region', 'bounds'],
        'additionalProperties': True,
        'properties': {
            'send_payload_to_current_node': {'type': 'boolean'},
            'api_key': {'type': 'string'},
            'query_term': {'type': 'string'},
            'language': {'type': 'string'},
            'region': {'type': 'string'},
            'bounds': {
                'type': 'array',
                'items': {'$ref': '#/definitions/rect'}
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
            },
            'rect': {
                'type': 'array',
                'items': {'$ref': '#/definitions/gps'},
                'minItems': 2,
                'maxItems': 2
            }
        }
    }


@PureContentModule
def run(content_config, unused_env, variables):
    """
    content_config schema:

    Platform dependent message:
    {
        'send_payload_to_current_node': False,
        'api_key': 'google geocoding api key',
        'query_term': 'query term',
        'language': 'zh_TW',
        'region': 'tw',
        'bounds': [
            {'lat': 23.816576, 'long': 119.781068},
            {'lat': 25.314444, 'long': 122.053702}
        ],
        'center': {'lat': 23.816576, 'long': 122.053702}
    }
    """
    query_term = Resolve(content_config['query_term'], variables)

    # Remove stop words
    query_term = re.sub(STOP_WORDS, '', query_term)

    cfg = content_config

    api = GoogleMapsPlaceAPI(content_config['api_key'])

    py_bounds = []
    for b in cfg.get('bounds', []):
        py_bounds.append([(b[0]['lat'], b[0]['long']),
                          (b[1]['lat'], b[1]['long'])])

    results = api.query_top_n(3, query_term, cfg['language'],
                              cfg['region'], py_bounds,
                              cfg.get('center', None))

    in_currrent = content_config['send_payload_to_current_node']

    if not results:
        m = Message(u'對不起，我找不到這個地址, 請重新輸入 >_<')
    elif len(results) == 1:
        m = Message(u'你指的是「%s」嗎？' % results[0]['address'])
        m.add_quick_reply(
            Message.QuickReply(Message.QuickReplyType.TEXT, u'是',
                               payload=LocationPayload(results[0]['location'],
                                                       in_currrent),
                               acceptable_inputs=[u'^對', '(?i)^y',
                                                  '(?i)ok']))
        m.add_quick_reply(
            Message.QuickReply(Message.QuickReplyType.TEXT, u'否',
                               payload=EventPayload('WRONG_ADDRESS', None,
                                                    in_currrent),
                               acceptable_inputs=[u'不', '(?i)^n']))
    else:
        m = Message(buttons_text=u'你指的是以下哪一個地址呢?')
        for r in results:
            m.add_button(Message.Button(Message.ButtonType.POSTBACK,
                                        r['address'],
                                        payload=LocationPayload(r['location'],
                                                                in_currrent)))
    return [m]
