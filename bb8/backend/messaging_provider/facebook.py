# -*- coding: utf-8 -*-
"""
    Facebook messaging provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import urllib

import jsonschema
import requests

from flask import g


FACEBOOK_API_URL = 'https://graph.facebook.com'

FACEBOOK_PROFILE_API_URL = 'https://graph.facebook.com/v2.6/%s'
FACEBOOK_MESSAGING_THREAD_SETTING = ('https://graph.facebook.com/v2.6/me/'
                                     'thread_settings')
FACEBOOK_MESSAGING_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
FACEBOOK_MESSAGING_API_RELATIVE_URL = 'v2.6/me/messages'


def get_config_schema():
    """Return platform config schema."""
    return {
        'type': 'object',
        'required': ['access_token'],
        'properties': {
            'access_token': {'type': 'string'},
        }
    }


def get_settings_schema():
    """Get settings schema."""
    return {
        'type': 'object',
        'properties': {
            'get_start_button': {'type': 'object'},
            'greeting_text': {'type': 'string'},
            'persistent_menu': {
                'type': 'array',
                'items': {'$ref': '#/definitions/button'}
            }
        },
        'definitions': {
            'button': {
                'oneOf': [{
                    'required': ['type', 'title', 'url'],
                    'additionalProperties': False,
                    'type': 'object',
                    'properties': {
                        'type': {'enum': ['web_url']},
                        'title': {'type': 'string'},
                        'url': {'type': 'string'}
                    }
                }, {
                    'required': ['type', 'title', 'payload'],
                    'additionalProperties': False,
                    'type': 'object',
                    'properties': {
                        'type': {'enum': ['postback']},
                        'title': {'type': 'string'},
                        'payload': {'type': ['string', 'object']}
                    }
                }]
            }
        }
    }


def apply_settings(config, settings):
    """Apply settings to platform."""
    try:
        jsonschema.validate(settings, get_settings_schema())
    except jsonschema.ValidationError as e:
        raise RuntimeError('Facebook settings schema validation failed: %s' %
                           e)

    greeting = settings.get('greeting_text', None)
    if greeting:
        set_greeting_text(config['access_token'], greeting)

    payload = settings.get('get_start_button', None)
    if payload:
        set_get_start_button(config['access_token'], payload)

    menu = settings.get('persistent_menu', None)
    if menu:
        set_persistent_menu(config['access_token'], menu)


def set_greeting_text(access_token, text):
    """Set greeting text."""
    response = requests.request(
        'POST',
        FACEBOOK_MESSAGING_THREAD_SETTING,
        params={
            'access_token': access_token
        },
        json={
            'setting_type': 'greeting',
            'greeting': text
        })

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))


def set_get_start_button(access_token, payload):
    """Set getting start button."""
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    response = requests.request(
        'POST',
        FACEBOOK_MESSAGING_THREAD_SETTING,
        params={
            'access_token': access_token
        },
        json={
            'setting_type': 'call_to_actions',
            'thread_state': 'new_thread',
            'call_to_actions': [
                {
                    'payload': payload
                }
            ]
        })

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))


def set_persistent_menu(access_token, menu_items):
    """Set persistent menu for the bot."""
    for item in menu_items:
        if (item['type'] == 'postback' and
                isinstance(item['payload'], dict)):
            item['payload'] = json.dumps(item['payload'])

    response = requests.request(
        'POST',
        FACEBOOK_MESSAGING_THREAD_SETTING,
        params={
            'access_token': access_token
        },
        json={
            'setting_type': 'call_to_actions',
            'thread_state': 'existing_thread',
            'call_to_actions': menu_items
        })

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))


def get_user_profile(platform, user_ident):
    """Get user profile information."""
    response = requests.request(
        'GET',
        FACEBOOK_PROFILE_API_URL % user_ident,
        params={
            'access_token': platform.config['access_token'],
            'fields': 'first_name,last_name,locale,timezone,gender'
        })

    if response.status_code != 200:
        ret = {
            'first_name': u'你好',
            'last_name': u'',
            'locale': 'zh_TW',
            'timezone': 8,
            'gender': 'Male'
        }
        return ret

    ret = response.json()

    # Some account does not have gender for some reason ... assume male
    if 'gender' not in ret:
        ret['gender'] = 'male'

    ret['gender'] = ret['gender'].title()
    return ret


def send_message_batch(user, messages):
    """Batch message sending."""
    batch = []
    for index, message in enumerate(messages):
        payload = {
            'recipient': json.dumps({'id': user.platform_user_ident}),
            'message': json.dumps(message.as_facebook_message()),
            'notification_type': message.notification_type.value
        }
        req = {
            'name': 'msg-%d' % index,
            'method': 'POST',
            'relative_url': FACEBOOK_MESSAGING_API_RELATIVE_URL,
            'body': urllib.urlencode(payload)
        }

        if index > 0:
            req['depends_on'] = 'msg-%d' % (index - 1)

        batch.append(req)

    response = requests.request(
        'POST',
        FACEBOOK_API_URL,
        params={
            'access_token': user.platform.config['access_token'],
            'batch': str(batch)
        }
    )

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))


def send_message(unused_user, messages):
    """Send message to the user."""
    if not hasattr(g, 'messages'):
        g.messages = []

    g.messages += messages


def flush_message(user):
    """Flush the message in the send queue."""
    if not hasattr(g, 'messages'):
        return

    send_message_batch(user, g.messages)


def push_message(user, messages):
    """Push message to user proactively."""
    return send_message_batch(user, messages)


def download_audio_as_data(unused_user, audio_payload):
    """Download audio file as data."""
    response = requests.get(audio_payload['url'], stream=True)

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))
    return response.raw.read()
