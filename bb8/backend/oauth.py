# -*- coding: utf-8 -*-
"""
    OAuth Helpers
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import re

import requests

from bb8 import config


def facebook_verify_token(access_token):
    facebook_app_access_token = '%s|%s' % (
        config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET)

    res = requests.get(
        'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
        % (access_token, facebook_app_access_token))
    res.raise_for_status()
    data = res.json()

    if (not data['data']['is_valid'] or
            data['data']['app_id'] != config.FACEBOOK_APP_ID):
        raise RuntimeError('The access token is invalid')

    return data['data']['user_id']


def facebook_get_long_lived_token(access_token):
    res = requests.get(
        'https://graph.facebook.com/oauth/access_token?'
        'grant_type=fb_exchange_token&client_id=%s&'
        'client_secret=%s&'
        'fb_exchange_token=%s' %
        (config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET, access_token))
    res.raise_for_status()
    m = re.search(r'access_token=([^&]*)', res.text)
    return m.group(1)
