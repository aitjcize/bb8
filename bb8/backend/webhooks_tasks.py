# -*- coding: utf-8 -*-
"""
    Webhook Tasks
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime

from flask import g, request

from bb8 import logger, celery, config, statsd
from bb8.backend.database import (DatabaseManager, User, Platform,
                                  Conversation, SenderEnum)
from bb8.backend.engine import Engine
from bb8.backend.message import UserInput
from bb8.backend.messaging import get_user_profile
from bb8.backend.messaging_provider import line
from bb8.backend.requestcontexttask import RequestContextTask

from bb8.tracking import track, TrackingInfo, send_ga_track_info


def add_user(platform, sender):
    """Add a new user into the system."""
    profile_info = get_user_profile(platform, sender)
    user = User(platform_id=platform.id,
                platform_user_ident=sender,
                last_seen=datetime.datetime.now(),
                **profile_info).add()
    DatabaseManager.commit()

    statsd.gauge('users', User.count(), tags=[config.ENV_TAG])
    track(TrackingInfo.Event(sender, '%s.User' % platform.type_enum.value,
                             'Add', profile_info['first_name']))
    return user


def store_conversation(user, message, sender_enum=SenderEnum.User):
    """Store message into conversation table."""
    if config.STORE_CONVERSATION:
        Conversation(user_id=user.id,
                     sender_enum=sender_enum,
                     messages=message,
                     timestamp=message['timestamp']).add()


# Type check is diabled (typing=False) because RequestContextTask piggyback
# request arguments through kwargs.
@celery.task(base=RequestContextTask, typing=False)
def facebook_webhook_task():
    with statsd.timed('facebook_webhook_task', tags=[config.ENV_TAG]):
        engine = Engine()

        for entry in request.json.get('entry', []):
            page_id = entry['id']
            platform = Platform.get_cached(page_id)

            if platform is None:
                raise RuntimeError('No associated platform found for Facebook '
                                   'Platform with page_id = %s' % page_id)

            bot = platform.bot
            if bot is None:
                raise RuntimeError('No associated bot found for Facebook '
                                   'Platform with page_id = %s' % page_id)

            g.ga_id = bot.ga_id

            # TODO(aitjcize): bot should always have a account in the future
            # even for our own bots (compose.ai).
            if bot.account and not bot.account.valid():
                # Account is not valid, don't process events for it.
                continue

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

                    store_conversation(user, messaging, SenderEnum.Manual)
                    engine.process_admin_reply(bot, user, user_input)
                else:
                    user = User.get_by(platform_id=platform.id,
                                       platform_user_ident=sender,
                                       eager=['platform'], single=True)
                    if not user:
                        user = add_user(platform, sender)

                    if user_input.ref:
                        track(TrackingInfo.Pageview(
                            sender, '/', user_input.ref))

                    store_conversation(user, messaging)
                    if user_input.valid():
                        engine.run(bot, user, user_input)

    # Don't measure the time of the GA call
    send_ga_track_info()


# Type check is diabled (typing=False) because RequestContextTask piggyback
# request arguments through kwargs.
@celery.task(base=RequestContextTask, typing=False)
def line_webhook_task(provider_ident):
    with statsd.timed('line_webhook_task', tags=[config.ENV_TAG]):
        engine = Engine()
        platform = Platform.get_cached(provider_ident)

        if platform is None:
            raise RuntimeError('no associate bot found for Line '
                               'Platform with ident = %s' % provider_ident)

        for entry in request.json.get('events', []):
            if entry['source']['type'] != 'user':
                if entry['source']['type'] == 'group':
                    line.leave_group(platform, entry['source']['groupId'])
                elif entry['source']['type'] == 'room':
                    line.leave_room(platform, entry['source']['roomId'])

                logger.warn('line_receive: only user source is supported '
                            'for now')
                continue

            sender = entry['source']['userId']
            bot = platform.bot
            g.ga_id = bot.ga_id

            user = User.get_by(platform_id=platform.id,
                               platform_user_ident=sender, single=True)
            if not user:
                user = add_user(platform, sender)

            user_input = UserInput.FromLineMessage(entry)

            store_conversation(user, entry)
            if user_input.valid():
                g.line_reply_token = entry['replyToken']
                engine.run(bot, user, user_input)

    # Don't measure the time of the GA call
    send_ga_track_info()
