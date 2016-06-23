# -*- coding: utf-8 -*-
"""
    Line messaging provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import requests


LINE_MESSAGING_API_URL = 'https://trialbot-api.line.me/v1/events'


def get_user_profile(platform, user_ident):
    ret = {
        'first_name': u'',
        'last_name': u'',
        'locale': 'zh_TW',
        'timezone': 8,
        'gender': 'male'
    }
    return ret


def send_message(user, messages):
    platform = user.platform
    headers = {
        'X-Line-ChannelID': platform.config['channel_id'],
        'X-Line-ChannelSecret': platform.config['channel_secret'],
        'X-Line-Trusted-User-With-ACL': platform.config['mid']
    }

    for message in messages:
        response = requests.request(
            'POST',
            LINE_MESSAGING_API_URL,
            headers=headers,
            json={
                'to': [user.platform_user_ident],
                'toChannel': 1383378250,  # Fixed value
                'eventType': '140177271400161403',  # Fixed value
                'content': message.as_line_message()
            }
        )

        if response.status_code != 200:
            raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                                response.text))
