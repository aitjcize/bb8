# -*- coding: utf-8 -*-
"""
    Show a button for testing postback
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (Message, SupportedPlatform,
                                    PureContentModule, ModuleTypeEnum)
from bb8.backend.message import TextPayload


def properties():
    return {
        'id': 'ai.compose.content.test.postback',
        'type': ModuleTypeEnum.Content,
        'name': 'show and parse postback',
        'description': 'show and parse postback',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {}


@PureContentModule
def run(unused_content_config, unused_env, unused_variables):
    m = Message()
    b = Message.Bubble('Tap postback')
    b.add_button(Message.Button(Message.ButtonType.POSTBACK, 'Postback',
                                payload=TextPayload('PAYLOAD_TEXT')))
    m.add_bubble(b)
    return [m]
