# -*- coding: utf-8 -*-
"""
    Broadcast Related Functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time
from datetime import datetime

from sqlalchemy.exc import IntegrityError, InvalidRequestError

from bb8 import celery, logger
from bb8.backend.database import (Bot, Broadcast, BroadcastStatusEnum,
                                  DatabaseManager, DatabaseSession)
from bb8.backend.message import Message
from bb8.backend.messaging_tasks import broadcast_message_async

import jsonschema


class BroadcastUnmodifiableError(Exception):
    pass


def validate_broadcast_schema(broadcast_json):
    """Validate broadcast request schema."""
    try:
        jsonschema.validate(broadcast_json, Broadcast.schema())
        for message in broadcast_json['messages']:
            jsonschema.validate(message, Message.schema())
    except jsonschema.exceptions.ValidationError:
        logger.error('Validation failed for `broadcast_json\'!')
        raise


@celery.task
def broadcast_task(broadcast_id):
    with DatabaseSession():
        broadcast = Broadcast.get_by(id=broadcast_id, single=True)
        # The broadcast entry could be delted by user
        if not broadcast:
            return

        # Either broadcast in progress or already sent
        if broadcast.status != BroadcastStatusEnum.QUEUED:
            return

        # The user may have changed the broadcasting time, ignore it as it
        # should be automatically rescheduled.
        if broadcast.scheduled_time >= datetime.now():
            return

        broadcast.status = BroadcastStatusEnum.SENDING
        try:
            DatabaseManager.commit()
        except (InvalidRequestError, IntegrityError):
            # The broadcast task have changed during our modification, retry.
            DatabaseManager.rollback()
            return broadcast_task(broadcast_id)

        # Do the actually broadcast
        bot = Bot.get_by(id=broadcast.bot_id, account_id=broadcast.account_id,
                         single=True)

        # Bot may have been deleted
        if not bot:
            return

        messages = [Message.FromDict(m, register_mapping=False)
                    for m in broadcast.messages]
        broadcast_message_async(bot, messages)

        # pylint: disable=R0204
        broadcast.status = BroadcastStatusEnum.SENT


def schedule_broadcast(broadcast):
    """Schedule a broadcast."""
    broadcast_task.apply_async((broadcast.id,), eta=broadcast.scheduled_time)


def parse_broadcast(broadcast_json, to_broadcast_id=None):
    """Parse Broadcast from broadcast definition."""
    validate_broadcast_schema(broadcast_json)

    if callable(to_broadcast_id):
        to_broadcast_id = to_broadcast_id(broadcast_json)

    # Validate that the target bot is own by the same account.
    bot = Bot.get_by(id=broadcast_json['bot_id'],
                     account_id=broadcast_json['account_id'],
                     single=True)
    if not bot:
        raise RuntimeError('bot does not exist for broadcast')

    if broadcast_json['scheduled_time'] == 0:
        broadcast_json['scheduled_time'] = int(time.time())

    if to_broadcast_id:
        broadcast = Broadcast.get_by(id=to_broadcast_id, single=True)
        if broadcast.status != BroadcastStatusEnum.QUEUED:
            raise BroadcastUnmodifiableError

        # Update existing broadcast.
        logger.info(u'Updating existing Broadcast(id=%d, name=%s) ...',
                    to_broadcast_id, broadcast_json['name'])
        broadcast = Broadcast.get_by(id=to_broadcast_id, single=True)
        broadcast.bot_id = broadcast_json['bot_id']
        broadcast.name = broadcast_json['name']
        broadcast.messages = broadcast_json['messages']
        broadcast.scheduled_time = datetime.utcfromtimestamp(
            broadcast_json['scheduled_time'])
        broadcast.status = broadcast_json.get('status', broadcast.status)
    else:
        # Create a new broadcast.
        logger.info(u'Creating new Broadcast(name=%s) ...',
                    broadcast_json['name'])
        broadcast_json['scheduled_time'] = datetime.utcfromtimestamp(
            broadcast_json['scheduled_time'])
        broadcast = Broadcast(**broadcast_json).add()

    DatabaseManager.commit()
    schedule_broadcast(broadcast)

    return broadcast
