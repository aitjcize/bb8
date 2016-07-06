# -*- coding: utf-8 -*-
"""
    Chatbot webhooks
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime

from flask import request

from bb8 import config, app, logger
from bb8.tracking import track, TrackingInfo
from bb8.backend.database import User, Platform, PlatformTypeEnum
from bb8.backend.engine import Engine
from bb8.backend.messaging import get_user_profile
from bb8.backend.metadata import UserInput


def add_user(bot, platform, sender):
    """Add a new user into the system."""
    profile_info = get_user_profile(platform, sender)
    user = User(bot_id=bot.id, platform_id=platform.id,
                platform_user_ident=sender,
                last_seen=datetime.datetime.now(),
                **profile_info).add()
    user.commit()

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

            for messaging in entry['messaging']:
                sender = messaging['sender']['id']
                user = User.get_by(bot_id=bot.id, platform_id=platform.id,
                                   platform_user_ident=sender, single=True)
                if not user:
                    user = add_user(bot, platform, sender)

                user_input = UserInput.FromFacebookMessage(messaging)
                if user_input:
                    engine.step(bot, user, user_input)
    except Exception as e:
        logger.exception(e)

    return 'ok'


@app.route(config.LINE_WEBHOOK_PATH, methods=['POST'])
def line_receive():
    try:
        engine = Engine()

        for entry in request.json.get('result', []):
            content = entry['content']
            line_mid = entry['to'][0]
            sender = content['from']
            platform = Platform.get_by(type_enum=PlatformTypeEnum.Line,
                                       provider_ident=line_mid, single=True)
            if platform is None:
                raise RuntimeError('no associate bot found for Line '
                                   'Platform with mid = %s' % line_mid)
            bot = platform.bot

            user = User.get_by(bot_id=bot.id, platform_id=platform.id,
                               platform_user_ident=sender, single=True)
            if not user:
                user = add_user(bot, platform, sender)

            user_input = UserInput.FromLineMessage(content)
            if user_input:
                engine.step(bot, user, user_input)
    except Exception as e:
        logger.exception(e)

    return 'ok'
