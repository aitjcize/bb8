# -*- coding: utf-8 -*-
"""
    Broadcast API Endpoint
    ~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify, request

from bb8 import app, logger
from bb8.api.error import AppError
from bb8.api.middlewares import login_required
from bb8.backend.broadcast import BroadcastUnmodifiableError, parse_broadcast
from bb8.backend.database import (DatabaseManager, Broadcast,
                                  BroadcastStatusEnum)
from bb8.constant import HTTPStatus, CustomError


def get_account_broadcast_by_id(broadcast_id):
    broadcast = Broadcast.get_by(id=broadcast_id, account_id=g.account.id,
                                 single=True)
    if broadcast is None:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'broadcast_id: %d not found' % broadcast_id)
    return broadcast


@app.route('/api/bots/<int:bot_id>/broadcasts', methods=['GET'])
@login_required
def list_broadcasts(bot_id):
    """List all broadcasts."""
    broadcasts = Broadcast.get_by(bot_id=bot_id, account_id=g.account.id)
    return jsonify(broadcasts=[b.to_json() for b in broadcasts])


@app.route('/api/broadcasts', methods=['POST'])
@login_required
def create_broadcast():
    """Create a new broadcast."""
    try:
        broadcast_json = request.json
        broadcast_json['account_id'] = g.account.id
        broadcast = parse_broadcast(broadcast_json)
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Broadcast create request failed')
    DatabaseManager.commit()
    return jsonify(broadcast.to_json())


@app.route('/api/broadcasts/<int:broadcast_id>', methods=['GET'])
@login_required
def show_broadcast(broadcast_id):
    broadcast = get_account_broadcast_by_id(broadcast_id)
    return jsonify(broadcast.to_json(['messages']))


@app.route('/api/broadcasts/<int:broadcast_id>', methods=['PUT'])
@login_required
def update_broadcast(broadcast_id):
    """Update a broadcast."""
    broadcast = get_account_broadcast_by_id(broadcast_id)
    try:
        broadcast_json = request.json
        broadcast_json['account_id'] = g.account.id
        parse_broadcast(broadcast_json, broadcast.id)
    except BroadcastUnmodifiableError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Broadcast not modifiable')
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Broadcast update request failed')
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/broadcasts/<int:broadcast_id>', methods=['DELETE'])
@login_required
def delete_broadcast(broadcast_id):
    """Delete a broadcast."""
    broadcast = get_account_broadcast_by_id(broadcast_id)
    if broadcast.status == BroadcastStatusEnum.SENT:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Broadcast not deletable')
    broadcast.delete()
    DatabaseManager.commit()
    return jsonify(message='ok')
