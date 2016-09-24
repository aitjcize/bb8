# -*- coding: utf-8 -*-
"""
    Passthrough module
    ~~~~~~~~~~~~~~~~~~

    Pass through next node without any action.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.database import Bot

from bb8.backend.module_api import (BroadcastMessage, ParseResult, LinkageItem,
                                    SupportedPlatform, Message, Memory)


def get_module_info():
    return {
        'id': 'ai.compose.parser.core.composeai',
        'name': 'Composeai',
        'description': 'Compose.ai bot parser',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'composeai',
        'ui_module_name': 'composeai',
        'variables': [],
    }


def schema():
    return {}


def run(unused_parser_config, user_input, unused_as_root):
    """
    {
      "links": [
        {
          "action_ident": "continue",
          "end_node_id": null,
          "ack_message": ""
        },
        {
          "action_ident": "done",
          "end_node_id": "[[root]]",
          "ack_message": ""
        }
      ]
    }
    """
    if user_input.text:
        if u'重設' in user_input.text or 'reset' in user_input.text.lower():
            Memory.Clear()
            return ParseResult(ack_message=u'讓我們重新開始吧!')

    if user_input.event:
        event = user_input.event
        if event.key == 'CONTROL_FLOW':
            if event.value == 'reset':
                Memory.Clear()
                return ParseResult('done', ack_message=u'放棄操作')
        elif event.key == 'SELECT_BOT':
            Memory.Set('bot', event.value)
        elif event.key == 'SELECT_OP':
            Memory.Set('operation', event.value)
        elif event.key == 'MESSAGE_INPUT':
            if event.value == 'done':
                Memory.Set('status', 'preview_message')
            elif event.value == 'restart':
                Memory.Set('broadcast_message', None)
                Memory.Set('status', None)
        elif event.key == 'CONFIRM_MESSAGE':
            if event.value:
                bot = Bot.get_by(id=Memory.Get('bot'), single=True)
                if not bot:
                    return ParseResult(ack_message=u'發生錯誤，找不到對應的'
                                                   u'機器人')
                msgs = [Message.FromDict(raw_msg)
                        for raw_msg in Memory.Get('broadcast_message')]
                BroadcastMessage(bot, msgs)
                Memory.Clear()
                return ParseResult('done', ack_message=u'您的訊息已送出!')
            else:
                Memory.Set('broadcast_message', None)

    status = Memory.Get('status')
    if status == 'input_broadcast_message':
        broadcast_message = Memory.Get('broadcast_message') or []
        broadcast_message.append(user_input.raw_message)
        Memory.Set('broadcast_message', broadcast_message)

    return ParseResult('continue', skip_content_module=False)


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('continue', None))
    links.append(LinkageItem('done', parser_config['done']))
    return links
