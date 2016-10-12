# -*- coding: utf-8 -*-
"""
    Chatbot webhooks
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import datetime
import hashlib
import hmac

from flask import request, g

from bb8 import config, app, logger
from bb8.tracking import track, TrackingInfo
from bb8.backend.database import (DatabaseManager, User, Platform,
                                  PlatformTypeEnum)
from bb8.backend.engine import Engine
from bb8.backend.messaging import get_user_profile
from bb8.backend.messaging_provider import line
from bb8.backend.metadata import UserInput


def add_user(platform, sender):
    """Add a new user into the system."""
    profile_info = get_user_profile(platform, sender)
    user = User(platform_id=platform.id,
                platform_user_ident=sender,
                last_seen=datetime.datetime.now(),
                **profile_info).add()
    DatabaseManager.commit()

    track(TrackingInfo.Event(sender, '%s.User' % platform.type_enum.value,
                             'Add', profile_info['first_name']))
    return user


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['GET'])
def facebook_challenge():
    """Facebook Bot API challenge."""
    if (request.args['hub.verify_token'] ==
            config.FACEBOOK_WEBHOOK_VALIDATION_TOKEN):
        return request.args['hub.challenge']
    return 'Error, wrong validation token'


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['POST'])
def facebook_receive():
    """Facebook Bot API receive."""
    # TODO(aitjcize): remove this in production
    # Facebook throttles message sending when it found out webhook fails. To
    # prevent throttling, let's catch all exception and manually log them for
    # now.

    try:
        engine = Engine()

        for entry in request.json.get('entry', []):
            page_id = entry['id']
            platform = Platform.get_by(type_enum=PlatformTypeEnum.Facebook,
                                       provider_ident=page_id, single=True)
            if platform is None:
                raise RuntimeError('no associate bot found for Facebook '
                                   'Platform with page_id = %s' % page_id)

            bot = platform.bot
            g.ga_id = bot.ga_id

            for messaging in entry['messaging']:
                msg = messaging.get('message', None)
                sender = messaging['sender']['id']
                recipient = messaging['recipient']['id']
                user_input = UserInput.FromFacebookMessage(messaging)

                if msg and msg.get('is_echo'):
                    # Ignore message sent by ourself
                    if msg.get('app_id', None):
                        continue
                    user = User.get_by(platform_id=platform.id,
                                       platform_user_ident=recipient,
                                       single=True)
                    engine.process_admin_reply(bot, user, user_input)
                else:
                    user = User.get_by(platform_id=platform.id,
                                       platform_user_ident=sender,
                                       eager=['platform'], single=True)
                    if not user:
                        user = add_user(platform, sender)

                    if user_input:
                        engine.step(bot, user, user_input)
    except Exception as e:
        logger.exception(e)

    return 'ok'


@app.route(config.LINE_WEBHOOK_PATH, methods=['POST'])
def line_receive(provider_ident):
    """LINE Bot API receive."""
    try:
        engine = Engine()

        for entry in request.json.get('events', []):
            if entry['source']['type'] != 'user':
                raise RuntimeError('line_receive: only user source is support '
                                   'for now')

            sender = entry['source']['userId']
            platform = Platform.get_by(provider_ident=provider_ident,
                                       single=True)
            if platform is None:
                raise RuntimeError('no associate bot found for Line '
                                   'Platform with ident = %s' % provider_ident)
            digest = hmac.new(str(platform.config['channel_secret']),
                              request.data, hashlib.sha256).digest()
            signature = base64.b64encode(digest)

            if signature != request.headers['X-Line-Signature']:
                raise RuntimeError('line_receive: failed to verify message')

            bot = platform.bot

            user = User.get_by(platform_id=platform.id,
                               platform_user_ident=sender, single=True)
            if not user:
                user = add_user(platform, sender)

            user_input = UserInput.FromLineMessage(entry)
            if user_input:
                g.line_reply_token = entry['replyToken']
                g.line_messages = []
                engine.step(bot, user, user_input)
                line.flush_message(platform)
    except Exception as e:
        logger.exception(e)

    return 'ok'
