# -*- coding: utf-8 -*-
"""
    Common handler for requests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import request

from bb8 import config, app
from bb8.backend.database import User, Platform
from bb8.backend.engine import Engine
from bb8.backend.metadata import UserInput


@app.route(config.FACEBOOK_WEBHOOK_PATH + '/<platform_id>', methods=['GET'])
def challenge(platform_id):
    platform = Platform.get_by(id=platform_id, single=True)
    if (request.args['hub.verify_token'] ==
            platform.config['validation_token']):
        return request.args['hub.challenge']
    return 'Error, wrong validation token'


@app.route(config.FACEBOOK_WEBHOOK_PATH + '/<platform_id>', methods=['POST'])
def receive(platform_id):
    platform = Platform.get_by(id=platform_id, single=True)
    bot = platform.bot
    engine = Engine()

    for entry in request.json['entry']:
        messagings = entry['messaging']
        for message in messagings:
            sender = message['sender']['id']

            user = User.get_by(bot_id=bot.id, platform_id=platform.id,
                               platform_user_ident=sender, single=True)
            if not user:
                user = User(bot_id=bot.id, platform_id=platform.id,
                            platform_user_ident=sender, last_seen=0).add()
                user.commit()

            if message.get('message'):
                text = message['message'].get('text')
                if text:
                    engine.step(bot, user, UserInput(text))

    return 'ok'


@app.route('/')
def index():
    return 'Hello, world!'
