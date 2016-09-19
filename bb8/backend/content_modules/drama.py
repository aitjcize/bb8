# -*- coding: utf-8 -*-
"""
    Drama Subscription Service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Drama module

    Copyright 2016 bb8 Authors
"""


import grpc

from bb8.backend.module_api import (Message, GetgRPCService, GetUserId,
                                    EventPayload, SupportedPlatform)

GRPC_TIMEOUT = 5
MAX_KEYWORDS = 7
DEFAULT_N_ITEMS = 7


def get_module_info():
    return {
        'id': 'ai.compose.content.third_party.drama',
        'name': 'drama',
        'description': 'Drama service',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'drama',
        'ui_module_name': 'drama',
    }


def schema():
    return {
        'type': 'object',
        'required': ['mode'],
        'properties': {
            'mode': {
                'enum': [
                    'default',
                    'trending_kr',
                    'trending_jp',
                    'trending_tw',
                    'trending_cn',
                    'subscribe',
                ]
            },
        }
    }


class DramaInfo(object):
    """Interface for querying drama content"""

    def __init__(self):
        pb2_module, addr = GetgRPCService('drama')
        channel = grpc.insecure_channel('%s:%d' % addr)
        self._stub = pb2_module.DramaInfoStub(channel)
        self._pb2_module = pb2_module

    def get_default_image(self):
        return 'http://i.imgur.com/xa9wSAU.png'

    def get_trending(self, user_id, country='kr', count=DEFAULT_N_ITEMS):
        return self._stub.Trending(
            self._pb2_module.TrendingRequest(
                user_id=user_id,
                country=country,
                count=count,
            ), GRPC_TIMEOUT).dramas

    def subscribe(self, user_id, drama_id):
        self._stub.Subscribe(
            self._pb2_module.SubscribeRequest(
                user_id=user_id, drama_id=drama_id), GRPC_TIMEOUT)

    def search(self, user_id, term):
        return self._stub.Search(
            self._pb2_module.SearchRequest(
                user_id=user_id, term=term
            ), GRPC_TIMEOUT).dramas


drama_info = DramaInfo()


def render_cards(dramas):
    """Render cards given a list of new dramas"""
    if not len(dramas):
        return [Message(u'找不到你要的劇喔！')]

    m = Message()
    for d in dramas:
        image_url = (d.image_url if d.image_url != '' else
                     drama_info.get_default_image())
        b = Message.Bubble(d.name,
                           image_url=image_url,
                           subtitle=d.description)
        b.add_button(Message.Button(
            Message.ButtonType.POSTBACK,
            u'追蹤我！', payload=EventPayload('SUBSCRIBE', {
                'drama_id': d.id,
            }, False)))
        m.add_bubble(b)
    return [m]


def run(content_config, unused_env, variables):
    user_id = GetUserId()

    if content_config['mode'] == 'subscribe':
        event = variables['event']
        drama_info.subscribe(user_id, event.value['drama_id'])
        return [Message(u'謝謝您的追蹤，'
                        u'我們會在有更新的時候通知您')]

    country = content_config['mode'].replace('trending_', '')
    return render_cards(drama_info.get_trending(user_id, country=country))
