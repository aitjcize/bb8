# -*- coding: utf-8 -*-
"""
    Compose.ai Control Module
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g
from bb8.backend.database import Bot

from bb8.backend.module_api import (Message, Memory, SupportedPlatform,
                                    EventPayload, ModuleTypeEnum,
                                    PureContentModule)


def properties():
    return {
        'id': 'ai.compose.content.core.composeai',
        'type': ModuleTypeEnum.Content,
        'name': 'Compose.ai Control',
        'description': 'Control interface for compose.ai',
        'supported_platform': SupportedPlatform.All,
        'variables': []
    }


def schema():
    return {
        'type': 'object',
        'required': ['bot_admins'],
        'properties': {
            'bot_admins': {
                'type': 'object',
                'patternProperties': {
                    '[0-9]+': {
                        'type': 'array',
                        'itme': {'type': 'integer'}
                    }
                }
            }
        }
    }


@PureContentModule
def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
        "bot_admins": {
            "platform_user_ident_1": ["bot_id_1", "bot_id_2" ..],
            ...
        }
    }
    """
    user = g.user

    bots = content_config['bot_admins'].get(user.platform_user_ident)
    if not bots:
        return []

    bot = Memory.Get('bot')
    if not bot:
        msgs = [Message(u'嗨 {{user.first_name}}，你想要操作哪隻機器人呢？',
                        variables=variables)]
        page = 1
        m = Message()
        msgs.append(m)
        bubble = Message.Bubble('第 %d 頁' % page)

        for bot_id in bots:
            bot = Bot.get_by(id=bot_id, single=True)
            if not bot:
                continue

            bubble.add_button(Message.Button(
                Message.ButtonType.POSTBACK, title=bot.name,
                payload=EventPayload('SELECT_BOT', bot_id)))

            if len(bubble.buttons) == 3:
                m.add_bubble(bubble)
                page += 1
                bubble = Message.Bubble(u'第 %d 頁' % page)

        if len(bubble.buttons):
            m.add_bubble(bubble)

        msgs[-1].add_quick_reply(Message.QuickReply(
            Message.QuickReplyType.TEXT,
            u'放棄', payload=EventPayload('CONTROL_FLOW', 'reset'),
            acceptable_inputs=['(?i)giveup', '(?i)reset']))
        return msgs

    operation = Memory.Get('operation')
    if not operation:
        m = Message(buttons_text=u'你想要執行什麼動作呢？')
        m.add_button(Message.Button(
            Message.ButtonType.POSTBACK, title=u'廣播訊息',
            payload=EventPayload('SELECT_OP', 'broadcast')))
        m.add_button(Message.Button(
            Message.ButtonType.POSTBACK, title=u'放棄',
            payload=EventPayload('CONTROL_FLOW', 'reset')))
        return [m]

    if operation == 'broadcast':
        broadcast_message = Memory.Get('broadcast_message')
        status = Memory.Get('status')
        if status == 'input_broadcast_message':
            m = Message(u'你可以繼續輸入下一則訊息:')
            m.add_quick_reply(Message.QuickReply(
                Message.QuickReplyType.TEXT,
                u'完成', payload=EventPayload('MESSAGE_INPUT', 'done'),
                acceptable_inputs=[u'好了', u'(?i)done', '(?i)y']))
            m.add_quick_reply(Message.QuickReply(
                Message.QuickReplyType.TEXT,
                u'重來', payload=EventPayload('MESSAGE_INPUT', 'restart'),
                acceptable_inputs=[u'好了', u'(?i)restart', '(?i)cancel']))
            m.add_quick_reply(Message.QuickReply(
                Message.QuickReplyType.TEXT,
                u'放棄', payload=EventPayload('CONTROL_FLOW', 'reset'),
                acceptable_inputs=['(?i)giveup', '(?i)reset']))
            return [m]
        elif not broadcast_message:
            Memory.Set('status', 'input_broadcast_message')
            return [Message(u'請輸入你要廣播的訊息:')]
        elif status == 'preview_message':
            msgs = [Message(u'請確認你要廣播的訊息:')]
            for raw_msg in broadcast_message:
                msgs.append(Message.FromDict(raw_msg))

            m = msgs[-1]
            m.add_quick_reply(Message.QuickReply(
                Message.QuickReplyType.TEXT,
                u'確認', payload=EventPayload('CONFIRM_MESSAGE', True),
                acceptable_inputs=[u'是', '(?i)y', '(?i)ok']))
            m.add_quick_reply(Message.QuickReply(
                Message.QuickReplyType.TEXT,
                u'取消', payload=EventPayload('CONFIRM_MESSAGE', False),
                acceptable_inputs=[u'是', '(?i)no', '(?i)cancel']))

            return msgs

    return [Message(u'錯誤的操作')]
