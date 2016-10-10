# -*- coding: utf-8 -*-
"""
    Line messaging provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import requests

from flask import g


LINE_MESSAGE_REPLY_API_URL = 'https://api.line.me/v2/bot/message/reply'


def get_config_schema():
    """Return platform config schema."""
    return {
        'type': 'object',
        'required': ['access_token', 'channel_secret'],
        'properties': {
            'access_token': {'type': 'string'},
            'channel_secret': {'type': 'string'},
        }
    }


def get_settings_schema():
    """Get settings schema."""
    return {}


def apply_settings(unused_config, unused_settings):
    """Apply settings to platform."""
    pass


def get_user_profile(unused_platform, unused_user_ident):
    """Get user profile information."""
    ret = {
        'first_name': u'你好',
        'last_name': u'',
        'locale': 'zh_TW',
        'timezone': 8,
        'gender': 'Male'
    }
    return ret


def send_message(unused_user, messages):
    """Send message to the platform."""
    g.line_messages += messages  # pylint: disable=E1101


def flush_message(platform):
    """Flush the message and send it to user."""
    headers = {
        'Authorization': 'Bearer %s' % platform.config['access_token']
    }

    response = requests.request(
        'POST',
        LINE_MESSAGE_REPLY_API_URL,
        headers=headers,
        json={
            'replyToken': g.line_reply_token,
            # pylint: disable=E1101
            'messages': [m.as_line_message() for m in g.line_messages]
        }
    )

    if response.status_code != 200:
        text = response.text.replace(u'\xa0', '\n')
        raise RuntimeError('HTTP %d: %s' % (response.status_code, text))
