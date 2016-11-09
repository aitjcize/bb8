# -*- coding: utf-8 -*-
"""
    Drama Subscription Service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


import grpc

from bb8.backend.content_modules.lib.numbers_parsing_utils import (
    convert_to_arabic_numbers)
from bb8.backend.module_api import (CacheImage, Message, EventPayload,
                                    GetgRPCService, GetUserId,
                                    SupportedPlatform, Resolve, Memory,
                                    TrackedURL)


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
                    'prompt',
                    'trending_kr',
                    'trending_jp',
                    'trending_tw',
                    'trending_cn',
                    'subscribe',
                    'unsubscribe',
                    'search',
                    'get_history',
                    'search_episode',
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

    def unsubscribe(self, user_id, drama_id):
        self._stub.Unsubscribe(
            self._pb2_module.UnsubscribeRequest(
                user_id=user_id, drama_id=drama_id), GRPC_TIMEOUT)

    def search(self, user_id, term, count):
        return self._stub.Search(
            self._pb2_module.SearchRequest(
                user_id=user_id, term=term, count=count
            ), GRPC_TIMEOUT).dramas

    def get_history(self, drama_id, from_episode, count=7, backward=False):
        return self._stub.GetHistory(
            self._pb2_module.HistoryRequest(
                drama_id=drama_id,
                from_episode=from_episode,
                count=count,
                backward=backward
            ), GRPC_TIMEOUT).episodes

    def get_episode(self, drama_id, serial_number):
        return self._stub.GetEpisode(
            self._pb2_module.GetEpisodeRequest(
                drama_id=drama_id,
                serial_number=serial_number
            ), GRPC_TIMEOUT)


def render_dramas(dramas):
    """Render cards given a list of dramas"""
    if not len(dramas):
        return Message(u'找不到你要的劇喔！')

    m = Message()
    for d in dramas:
        b = Message.Bubble(d.name,
                           image_url=CacheImage(d.image_url),
                           subtitle=d.description)
        if d.subscribed:
            b.add_button(Message.Button(
                Message.ButtonType.POSTBACK,
                u'取消追蹤', payload=EventPayload('UNSUBSCRIBE', {
                    'drama_id': d.id,
                }, False)))
        else:
            b.add_button(Message.Button(
                Message.ButtonType.POSTBACK,
                u'追蹤我', payload=EventPayload('SUBSCRIBE', {
                    'drama_id': d.id,
                }, False)))

        b.add_button(Message.Button(
            Message.ButtonType.POSTBACK,
            u'我想看前幾集',
            payload=EventPayload(
                'GET_HISTORY', {
                    'drama_id': d.id,
                    'from_episode': 0,
                    'backward': True,
                })))
        b.add_button(Message.Button(Message.ButtonType.ELEMENT_SHARE))
        m.add_bubble(b)
    return m


def render_episodes(episodes, variables):
    """Render cards given a list of episodes"""
    if not len(episodes):
        return [Message(u'沒有更多的集數可以看囉 :(')]

    m = Message()
    for ep in episodes:
        b = Message.Bubble(ep.drama_name + u'第 %d 集' % ep.serial_number,
                           image_url=CacheImage(ep.image_url),
                           subtitle=ep.description)

        b.add_button(Message.Button(
            Message.ButtonType.WEB_URL,
            u'帶我去看',
            url=TrackedURL(ep.link, 'WatchButton'),
            variables=variables))
        b.add_button(Message.Button(
            Message.ButtonType.POSTBACK,
            u'我想看前幾集',
            payload=EventPayload(
                'GET_HISTORY', {
                    'drama_id': ep.drama_id,
                    'from_episode': ep.serial_number,
                    'backward': True,
                })))
        m.add_bubble(b)

    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'第1集'))
    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'熱門韓劇'))
    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'熱門日劇'))
    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'熱門台劇'))
    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'熱門陸劇'))
    m.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'通知設定'))

    return [m]


def run(content_config, unused_env, variables):
    drama_info = DramaInfo()
    n_items = content_config.get('n_items', DEFAULT_N_ITEMS)
    user_id = GetUserId()

    def append_categories_to_quick_reply(m):
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'荼蘼'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'The K2 第十集'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'熱門韓劇'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'熱門日劇'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'熱門台劇'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'熱門陸劇'))
        m.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, u'通知設定'))
        return [m]

    if content_config['mode'] == 'subscribe':
        event = variables['event']
        drama_id = event.value['drama_id']
        Memory.Set('last_query_drama_id', drama_id)
        drama_info.subscribe(user_id, drama_id)

        episodes = drama_info.get_history(drama_id=drama_id,
                                          from_episode=0,
                                          backward=True)
        return ([Message(u'謝謝您的追蹤，'
                         u'我們會在有更新的時候通知您！'),
                 Message(u'在等待的同時，'
                         u'您可以先看看之前的集數喲！')] +
                render_episodes(episodes, variables))

    if content_config['mode'] == 'unsubscribe':
        event = variables['event']
        drama_id = event.value['drama_id']
        drama_info.unsubscribe(user_id, drama_id)

        return [Message(u'已成功取消訂閱')]

    if content_config['mode'] == 'get_history':
        event = variables['event']
        drama_id = event.value['drama_id']
        Memory.Set('last_query_drama_id', drama_id)
        from_episode = event.value['from_episode']
        backward = event.value['backward']
        episodes = drama_info.get_history(drama_id=drama_id,
                                          from_episode=from_episode,
                                          backward=backward)

        return render_episodes(episodes, variables)

    if content_config['mode'] == 'prompt':
        m = Message(u'你比較喜歡以下的什麼劇呢？')
        append_categories_to_quick_reply(m)
        return [m]

    country = content_config['mode'].replace('trending_', '')
    if content_config['mode'] == 'search':
        query_term = Resolve(content_config['query_term'], variables)
        dramas = drama_info.search(user_id, query_term, n_items)
        if dramas:
            if len(dramas) == 1:
                Memory.Set('last_query_drama_id', dramas[0].id)
            m = render_dramas(dramas)
            append_categories_to_quick_reply(m)
            return [m]
        m = Message(u'找不到耶！你可以換個關鍵字或試試熱門的類別：')
        append_categories_to_quick_reply(m)
        return [m]

    if content_config['mode'] == 'search_episode':
        if len(variables['matches']) == 3:
            dramas = drama_info.search(user_id, variables['matches'][1], 1)
            if dramas:
                Memory.Set('last_query_drama_id', dramas[0].id)

        drama_id = Memory.Get('last_query_drama_id')
        if drama_id:
            try:
                try:
                    serial_number = int(Resolve(content_config['episode'],
                                                variables))
                except ValueError:
                    serial_number = convert_to_arabic_numbers(
                        Resolve(content_config['episode'], variables))
                episode = drama_info.get_episode(drama_id, serial_number)
            except Exception:
                return [Message('沒有這一集喔')]
            return render_episodes([episode], variables)
        else:
            return [Message('請先告訴我你要查的劇名')]

    m = render_dramas(drama_info.get_trending(user_id, country=country))
    append_categories_to_quick_reply(m)
    return [m]
