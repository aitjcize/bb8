# -*- coding: utf-8 -*-
"""
    Content recommendation
    ~~~~~~~~~~~~~~~~~~~~~~
    News content module

    Copyright 2016 bb8 Authors
"""


from grpc.beta import implementations

from bb8.backend.module_api import (Message, GetgRPCService, Resolve,
                                    EventPayload, TextPayload,
                                    SupportedPlatform, Render)

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

    def get_content(self, entry_link, char_offset=0, limit=320):
        cont = self._stub.GetContent(
            self._pb2_module.GetContentRequest(
                entry_link=entry_link,
                char_offset=char_offset,
                limit=limit),
            GRPC_TIMEOUT)
        return cont.content, cont.char_offset, cont.total_length

    def get_picture(self, entry_link, pic_index=0, unused_count=1):
        cont = self._stub.GetPicture(
            self._pb2_module.GetPictureRequest(
                entry_link=entry_link,
                pic_index=pic_index),
            GRPC_TIMEOUT)
        return cont.src, cont.alt, cont.pic_index

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
            content, char_offset, total_length = news_info.get_content(
                event.value['entry_link'], event.value['char_offset'])
            src, alt, pic_index = news_info.get_picture(
                event.value['entry_link'],
                event.value['pic_index'])
        except KeyError:
            return [Message(u'抱歉，有些東西出錯了，請再試一次！')]

        content_ended = char_offset == -1
        picture_ended = pic_index == -1
        all_ended = content_ended and picture_ended

        has_picture = src and alt
        has_content = content != ''

        progress = float(char_offset) / total_length * 100 \
            if char_offset >= 0 else 100.0

        msgs = []
        if has_content and not all_ended:
            m = Message()
            m.set_buttons_text(content)
            m.add_button(Message.Button(
                Message.ButtonType.POSTBACK,
                u'繼續讀 ({:.0f}%)'.format(progress),
                payload=EventPayload('GET_CONTENT', {
                    'entry_link': event.value['entry_link'],
                    'char_offset': char_offset,
                    'link': event.value['link'],
                    'pic_index': pic_index,
                }, False)))
            m.add_button(Message.Button(
                Message.ButtonType.WEB_URL, u'去網站讀',
                url=event.value['link']))
            msgs.append(m)
        elif has_content:
            msgs.append(Message(content))

        if has_picture:
            src_msg = Message(image_url=src)
            if alt.strip():
                alt_msg = Message()
                b = Message.Bubble(alt, subtitle=' ')
                # Only append button to the last message, so only append if
                # content is empty
                if not has_content and not all_ended:
                    b.add_button(Message.Button(
                        Message.ButtonType.POSTBACK,
                        u'繼續看圖 (文字已結束)',
                        payload=EventPayload('GET_CONTENT', {
                            'entry_link': event.value['entry_link'],
                            'char_offset': char_offset,
                            'link': event.value['link'],
                            'pic_index': pic_index,
                        }, False)))
                    b.add_button(Message.Button(
                        Message.ButtonType.WEB_URL, u'去網站讀',
                        url=event.value['link']))
                alt_msg.add_bubble(b)
                msgs = [src_msg, alt_msg] + msgs
            else:
                msgs = [src_msg] + msgs

        if all_ended:
            msg = Message()
            msg.set_buttons_text(u'這則新聞讀完囉！')
            msg.add_button(Message.Button(
                Message.ButtonType.POSTBACK,
                u'再推薦我一些！',
                payload=TextPayload(
                    Render("search {{q.query_term|last|fallback('')}}",
                           variables))))
            msgs.append(msg)

        return msgs

    if content_config['mode'] == 'get_by_source':
        source_name = Resolve(content_config['query_term'], variables)
        news = news_info.trending(source_name, 5)
    elif content_config['mode'] == 'search':
        query_term = Resolve(content_config['query_term'], variables)
        if query_term:
            news = news_info.search(query_term, 5)
        else:
            news = news_info.trending()
    elif content_config['mode'] == 'trending':
        news = news_info.trending()
    else:
        news = news_info.trending()

    if not len(news):
        return [Message(u'找不到你要的新聞喔！')]

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
                'entry_link': n.link,
                'char_offset': 0,
                'link': n.link,
                'pic_index': 0,
            }, False)))
        b.add_button(Message.Button(
            Message.ButtonType.WEB_URL, u'去網站讀',
            url=n.link))
        msg.add_bubble(b)

    return [msg]
