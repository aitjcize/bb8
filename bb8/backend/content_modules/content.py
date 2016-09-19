# -*- coding: utf-8 -*-
"""
    Content recommendation
    ~~~~~~~~~~~~~~~~~~~~~~
    News content module

    Copyright 2016 bb8 Authors
"""


import grpc

from bb8.backend.module_api import (Message, GetgRPCService, Resolve,
                                    EventPayload, SupportedPlatform,
                                    Render, GetUserId)

GRPC_TIMEOUT = 5
MAX_KEYWORDS = 7
DEFAULT_N_ITEMS = 7


def get_module_info():
    return {
        'id': 'ai.compose.content.core.content',
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
                    'prompt',
                    'trending',
                    'recommend',
                    'search',
                    'get_content',
                    'list_by_source',
                ]
            },
            'n_items': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 10
            },
            'query': {'type': 'string'},
        }
    }


class NewsInfo(object):
    """Interface for querying news content"""

    def __init__(self):
        pb2_module, addr = GetgRPCService('content')
        channel = grpc.insecure_channel('%s:%d' % addr)
        self._stub = pb2_module.ContentInfoStub(channel)
        self._pb2_module = pb2_module

    def get_default_image(self, source):
        source_default_images = {
            'storm': 'http://i.imgur.com/j1Kqrj1.png',
            'yahoo_rss': 'http://i.imgur.com/Q2Yfylc.jpg',
        }
        compose_default_image = 'http://i.imgur.com/xa9wSAU.png'
        return source_default_images.get(source, compose_default_image)

    def trending(self, user_id, source_name=None, count=5):
        return self._stub.Trending(
            self._pb2_module.TrendingRequest(
                user_id=user_id,
                source_name=source_name,
                count=count),
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

    def recommend(self, user_id, count=5):
        return self._stub.PersonalRecommend(
            self._pb2_module.RecommendRequest(
                user_id=user_id, count=count
            ), GRPC_TIMEOUT).entries

    def search(self, query, count=5):
        return self._stub.Search(
            self._pb2_module.SearchRequest(query=query, count=count),
            GRPC_TIMEOUT).entries

    def get_keywords(self, count=5):
        return self._stub.GetKeywords(
            self._pb2_module.GetKeywordsRequest(limit=count),
            GRPC_TIMEOUT).keywords

    def get_related_keywords(self, name, count=5):
        return self._stub.GetRelatedKeywords(
            self._pb2_module.GetRelatedKeywordsRequest(
                name=name, limit=count),
            GRPC_TIMEOUT).keywords


# Global NewsInfo instance for easy access
news_info = NewsInfo()


def add_quick_reply_keywords(message, show_related=False):
    """Install QuickReply keywords into message."""
    keywords = news_info.get_keywords(MAX_KEYWORDS)
    reply_kws = []
    if show_related:
        query_term = Render("{{q.query_term|last|fallback('')}}", {})
        related_kws = news_info.get_related_keywords(query_term, 3)

        reply_kws = [kw.name for kw in related_kws]
        for kw in keywords:
            if len(reply_kws) < MAX_KEYWORDS and kw.name not in reply_kws:
                reply_kws.append(kw.name)
    else:
        reply_kws += [kw.name for kw in keywords]

    for kw in reply_kws:
        message.add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT, kw))

    message.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'熱門新聞'))
    message.add_quick_reply(Message.QuickReply(
        Message.QuickReplyType.TEXT, u'搜尋'))


def render_cards(news):
    """Render cards given a list of new entries."""
    if not len(news):
        return [Message(u'找不到你要的新聞喔！')]

    m = Message()
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
                'pic_index': 1,
            }, False)))
        b.add_button(Message.Button(
            Message.ButtonType.WEB_URL, u'去網站讀',
            url=n.link))
        b.add_button(Message.Button(Message.ButtonType.ELEMENT_SHARE))
        m.add_bubble(b)

    add_quick_reply_keywords(m, True)
    return [m]


def run_get_content(variables):
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
        m = Message(buttons_text=content)
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
        m = Message(u'這則新聞讀完囉！')
        add_quick_reply_keywords(m, True)

        msgs.append(m)

    return msgs


def run(content_config, unused_env, variables):
    user_id = GetUserId()
    n_items = content_config.get('n_items', DEFAULT_N_ITEMS)

    if content_config['mode'] == 'get_content':
        return run_get_content(variables)

    if content_config['mode'] == 'list_by_source':
        source_name = Resolve(content_config['query_term'], variables)
        return render_cards(
            news_info.trending(user_id, source_name, n_items))

    elif content_config['mode'] == 'prompt':
        m = Message(u'想要知道什麼呢？今天這些字最夯！')
        add_quick_reply_keywords(m)
        return [m]

    elif content_config['mode'] == 'search':
        query_term = Resolve(content_config['query_term'], variables)
        return render_cards(
            (news_info.search(query_term, n_items)
             if query_term else news_info.trending(user_id)))

    return render_cards(news_info.trending(user_id))
