# -*- coding: utf-8 -*-
"""
    Show a button for testing postback
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, TextPayload


def get_module_info():
    return {
        'id': 'ai.compose.test.postback',
        'name': 'show and parse postback',
        'description': 'show and parse postback',
        'module_name': 'test.postback',
        'ui_module_name': 'postback',
    }


def run(unused_content_config, env, unused_variables):
    m = Message()
    b = Message.Bubble('Tap postback')
    b.add_button(Message.Button(Message.ButtonType.POSTBACK, 'Postback',
                                payload=TextPayload('PAYLOAD_TEXT', env)))
    m.add_bubble(b)
    return [m]
