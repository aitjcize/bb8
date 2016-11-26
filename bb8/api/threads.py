# -*- coding: utf-8 -*-
"""
    Thread API Endpoint
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify, request

import jsonschema

from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound

from bb8 import app
from bb8.api.error import AppError
from bb8.api.middlewares import login_required
from bb8.backend import messaging
from bb8.backend.database import (DatabaseManager, User, Platform,
                                  AccountUser, Conversation)
from bb8.backend.message import Message
from bb8.constant import HTTPStatus, CustomError


_DEFAULT_THREAD_LISTING_COUNT = 30

THREAD_UPDATE_SCHEMA = {
    'type': 'object',
    'properties': {
        'assignee': {'type': 'integer'},
        'status': {
            'enum': [
                'Read',
                'Unread',
                'Assigned',
                'Open',
                'Closed',
                'Archived',
            ]
        },
        'comment': {'type': 'string'}
    }
}

THREAD_POST_SCHEMA = {
    'type': 'object',
    'required': ['message'],
    'properties': {
        'message': {'type': 'object'}
    }
}


@app.route('/api/threads', methods=['GET'])
@login_required
def list_threads():
    """List all threads.

    Args:
        filter: 'platform_id:<id>', 'bot_id:<id>'
    """
    query = User.query(User).join(
        Platform, User.platform_id == Platform.id).filter(
            Platform.account_id == g.account.id)

    filter_ = request.args.get('filter')
    if filter_:
        if filter_.startswith('bot_id'):
            bot_id = int(filter_.split(':')[1])
            query = query.filter(Platform.bot_id == bot_id)
        elif filter_.startswith('platform_id'):
            platform_id = int(filter_.split(':')[1])
            query = query.filter(Platform.id == platform_id)

    return jsonify(threads=[user.to_json(['assignee', 'status', 'comment'])
                            for user in query.all()])


@app.route('/api/threads/<int:thread_id>', methods=['GET'])
@login_required
def show_thread(thread_id):
    """Show specific thread."""
    try:
        User.query(User).join(
            Platform, User.platform_id == Platform.id).filter(
                User.id == thread_id,
                Platform.account_id == g.account.id).one()
    except NoResultFound:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'No thread found')

    last_id = request.args.get('last_id')
    limit = request.args.get('limit', _DEFAULT_THREAD_LISTING_COUNT)
    offset = request.args.get('offset', 0)

    query = Conversation.query().filter_by(user_id=thread_id).order_by(
        desc(Conversation.timestamp), desc(Conversation.id))

    if last_id:
        query = query.filter(Conversation.id < last_id)

    query = query.limit(limit).offset(offset)
    return jsonify(conversation=[c.to_json() for c in query.all()])


@app.route('/api/threads/<int:thread_id>', methods=['PATCH'])
@login_required
def update_thread(thread_id):
    """Allow updating assignee, status and comment."""
    data = request.json
    try:
        jsonschema.validate(data, THREAD_UPDATE_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    if 'assignee' in data:
        assignee = AccountUser.get_by(id=data['assignee'],
                                      account_id=g.account.id,
                                      single=True)
        if assignee is None:
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_WRONG_PARAM,
                           'assignee does not exist')
    try:
        user = User.query(User).join(
            Platform, User.platform_id == Platform.id).filter(
                User.id == thread_id,
                Platform.account_id == g.account.id).one()
    except NoResultFound:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'No thread found')

    for field in ['assignee', 'status', 'comment']:
        if field in data:
            setattr(user, field, data[field])

    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/threads/<int:thread_id>', methods=['POST'])
@login_required
def post_thread(thread_id):
    """Post new messages to the thread."""
    data = request.json
    try:
        jsonschema.validate(data, THREAD_POST_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')
    try:
        user = User.query(User).join(
            Platform, User.platform_id == Platform.id).filter(
                User.id == thread_id,
                Platform.account_id == g.account.id).one()
    except NoResultFound:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'No thread found')

    try:
        messaging.push_message(user, Message.FromDict(data['message']),
                               g.account_user.id)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'Invalid message')
    DatabaseManager.commit()
    return jsonify(message='ok')
