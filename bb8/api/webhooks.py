# -*- coding: utf-8 -*-
"""
    Common handler for requests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
import urllib

from flask import request, make_response

from bb8 import config, app
from bb8.backend.database import User, Platform, PlatformTypeEnum
from bb8.backend.engine import Engine
from bb8.backend.metadata import UserInput

from bb8.backend.content_modules.youbike import GOOGLE_STATIC_MAP_API_KEY


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['GET'])
def challenge():
    if (request.args['hub.verify_token'] ==
            config.FACEBOOK_WEBHOOK_VALIDATION_TOKEN):
        return request.args['hub.challenge']
    return 'Error, wrong validation token'


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['POST'])
def receive():
    # TODO(wnhuang): remove this in production
    # Facebook throttles message sending when it found out webhook fails. To
    # prevent throttling, let's catch all exception and manually log them for
    # now.
    try:
        engine = Engine()

        for entry in request.json['entry']:
            page_id = entry['id']
            platform = Platform.get_by(type_enum=PlatformTypeEnum.Facebook,
                                       provider_ident=page_id, single=True)
            bot = platform.bot

            for message in entry['messaging']:
                sender = message['sender']['id']

                user = User.get_by(bot_id=bot.id, platform_id=platform.id,
                                   platform_user_ident=sender, single=True)
                if not user:
                    user = User(bot_id=bot.id, platform_id=platform.id,
                                platform_user_ident=sender, last_seen=0).add()
                    user.commit()

                user_input = None
                postback = message.get('postback')
                if postback:
                    user_input = UserInput(postback=postback)

                msg = message.get('message')
                if msg:
                    user_input = UserInput(msg)

                if user_input:
                    engine.step(bot, user, user_input)
    except Exception as e:
        logging.exception(e)

    return 'ok'


@app.route('/render_map')
def redirect_url():
    """Workaround facebooks 'bug', wher it remove multiple value with same key.
    We use facebook to pass the arguments, then request render from Google on
    behalf of it."""
    # TODO(aitjcize): move this else where... this is not part of bb8

    url = request.args.get('url', None)
    if not url:
        return 'No URL specified'

    url = urllib.unquote(url + '&key=' + GOOGLE_STATIC_MAP_API_KEY)
    h = urllib.urlopen(url)
    response = make_response(h.read())
    response.headers['content-type'] = h.headers['content-type']

    return response
