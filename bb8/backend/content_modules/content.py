# -*- coding: utf-8 -*-
"""
    Content recommendation
    ~~~~~~~~~~~~~~~~~~~~~~
    News content module

    Copyright 2016 bb8 Authors
"""


from grpc.beta import implementations

from bb8.backend.module_api import (Message, GetgRPCService, Resolve,
                                    EventPayload, SupportedPlatform)

GRPC_TIMEOUT = 5


def get_module_info():
    return {
        'id': 'ai.compose.core.content',
        'name': 'Content',
        'description': '',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'content',
        'ui_module_name': 'content',
    }


def schema():
    return {
        'type': 'object',
        'required': ['mode'],
        'properties': {
            'mode': {
                'enum': [
                    'trending',
                    'recommend',
                    'search',
                    'get_content',
                    'get_by_source',
                    'get_by_category',
                ]
            },
            'query': {'type': 'string'},
        }
    }


class NewsInfo(object):
    """Interface for querying news content"""

    def __init__(self):
        pb2_module, addr = GetgRPCService('content')
        channel = implementations.insecure_channel(*addr)
        self._stub = pb2_module.beta_create_ContentInfo_stub(channel)
        self._pb2_module = pb2_module

    def get_default_image(self, source):
        source_default_images = {
            'storm': 'http://i.imgur.com/n3aWMSS.png',
            'yahoo_rss': 'http://i.imgur.com/DSQpwUC.jpg',
        }
        compose_default_image = 'http://i.imgur.com/xa9wSAU.png'
        return source_default_images.get(source, compose_default_image)

    def trending(self, source_name='', count=5):
        return self._stub.Trending(
            self._pb2_module.TrendingRequest(
                source_name=source_name, count=count),
            GRPC_TIMEOUT).entries

    def get_content(self, entry_id, char_offset=0, limit=320):
        cont = self._stub.GetContent(
            self._pb2_module.GetContentRequest(
                entry_id=entry_id,
                char_offset=char_offset,
                limit=limit),
            GRPC_TIMEOUT)
        return cont.content, cont.char_offset

    def get_by_category(self, category_name, count=5):
        return self._stub.GetByCategory(
            self._pb2_module.GetByCategoryRequest(
                category_name=category_name, count=count),
            GRPC_TIMEOUT).entries

    def recommend(self, user_id, count=5):
        return self._stub.PersonalRecommend(
            self._pb2_module.RecommendRequest(
                user_id=user_id, count=count
            ), GRPC_TIMEOUT).entries

    def search(self, query, count=5):
        return self._stub.Search(
            self._pb2_module.SearchRequest(query=query, count=count),
            GRPC_TIMEOUT).entries


def run(content_config, unused_env, variables):
    news_info = NewsInfo()

    if content_config['mode'] == 'get_content':
        try:
            event = variables['event']
            content, char_offset = news_info.get_content(
                event.value['entry_id'],
                event.value['char_offset'])
        except KeyError:
            return [Message(u'抱歉，有些東西出錯了，請再試一次！')]

        if char_offset != -1:
            msg = Message()
            msg.set_buttons_text(content)
            msg.add_button(Message.Button(
                Message.ButtonType.POSTBACK,
                u'繼續讀', payload=EventPayload('GET_CONTENT', {
                    'entry_id': event.value['entry_id'],
                    'char_offset': char_offset,
                    'link': event.value['link'],
                }, False)))
            msg.add_button(Message.Button(
                Message.ButtonType.WEB_URL, u'去網站讀',
                url=event.value['link']))
            return [msg]
        msg = Message()
        msg.set_buttons_text(u'這則新聞讀完囉！')
        msg.add_button(Message.Button(
            Message.ButtonType.POSTBACK,
            u'再推薦我一些！', payload=EventPayload('TRENDING', {}, False)))
        return [Message(content), msg]

    if content_config['mode'] == 'get_by_source':
        source_name = Resolve(content_config['query_term'], variables)
        news = news_info.trending(source_name, 5)

    elif content_config['mode'] == 'search':
        query_term = Resolve(content_config['query_term'], variables)
        news = news_info.search(query_term, 5)

    elif content_config['mode'] == 'trending':
        news = news_info.trending()

    else:
        news = news_info.trending()

    if not len(news):
        return [Message(u'今天的新聞已經被你讀完囉，去做別的事吧！')]

    msg = Message()
    for n in news:
        image_url = (n.image_url if n.image_url != '' else
                     news_info.get_default_image(n.source))
        b = Message.Bubble(n.title,
                           image_url=image_url,
                           subtitle=n.description)
        b.add_button(Message.Button(
            Message.ButtonType.POSTBACK,
            u'在這讀', payload=EventPayload('GET_CONTENT', {
                'entry_id': n.id,
                'char_offset': 0,
                'link': n.link,
            }, False)))
        b.add_button(Message.Button(
            Message.ButtonType.WEB_URL, u'去網站讀',
            url=n.link))
        msg.add_bubble(b)
    return [msg]
