# -*- coding: utf-8 -*-
"""
    Broadcast Related Functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from datetime import datetime

from bb8 import logger
from bb8.backend.database import (Broadcast, BroadcastStatusEnum,
                                  DatabaseManager)
from bb8.backend.message import Message

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

    DatabaseManager.flush()
    return broadcast
