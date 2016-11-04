# -*- coding: utf-8 -*-
"""
    Line messaging provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
import requests

from flask import g


LINE_PROFILE_API_URL = 'https://api.line.me/v2/bot/profile/%s'
LINE_MESSAGE_REPLY_API_URL = 'https://api.line.me/v2/bot/message/reply'
LINE_MESSAGE_PUSH_API_URL = 'https://api.line.me/v2/bot/message/push'
LINE_GET_CONTENT_API_URL = 'https://api.line.me/v2/bot/message/%s/content'


LOG = logging.getLogger(__file__)


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


def get_user_profile(platform, user_ident):
    """Get user profile information."""
    headers = {
        'Authorization': 'Bearer %s' % platform.config['access_token']
    }

    response = requests.request(
        'GET',
        LINE_PROFILE_API_URL % user_ident,
        headers=headers)

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))

    api_ret = response.json()
    ret = {
        'first_name': api_ret['displayName'],
        'last_name': u'',
        'locale': 'zh_TW',
        'timezone': 8,
        'gender': 'Male'
    }
    return ret


def send_message(unused_user, messages):
    """Send message to the platform."""
    # pylint: disable=E1101
    if len(g.line_messages) < 5:
        g.line_messages += messages
    else:
        LOG.warning('line.send_message: maxinum number of messages(5) '
                    'reached, ignoring new messages!')


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


def push_message(user, messages):
    """Push message to user proactively."""
    headers = {
        'Authorization': 'Bearer %s' % user.platform.config['access_token']
    }

    response = requests.request(
        'POST',
        LINE_MESSAGE_PUSH_API_URL,
        headers=headers,
        json={
            'to': user.platform_user_ident,
            'messages': [m.as_line_message() for m in messages]
        }
    )

    if response.status_code != 200:
        text = response.text.replace(u'\xa0', '\n')
        raise RuntimeError('HTTP %d: %s' % (response.status_code, text))


def download_audio_as_data(user, audio_payload):
    """Download audio file as data."""
    headers = {
        'Authorization': 'Bearer %s' % user.platform.config['access_token']
    }

    response = requests.get(
        LINE_GET_CONTENT_API_URL % audio_payload,
        headers=headers, stream=True)

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))

    return response.raw.read()
