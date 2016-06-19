# -*- coding: utf-8 -*-
"""
    Facebook messaging provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import requests


FACEBOOK_MESSAGING_API_URL = 'https://graph.facebook.com/v2.6/me/messages'


def send_message(user, messages):
    for message in messages:
        response = requests.request(
            'POST',
            FACEBOOK_MESSAGING_API_URL,
            params={'access_token': user.platform.config['access_token']},
            json={
                'recipient': {'id': user.platform_user_ident},
                'message': message.as_facebook_message(),
                'notification_type': message.notification_type.value
            }
        )

        if response.status_code != 200:
            raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                                response.text))
