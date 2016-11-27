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
                                  AccountUser, Conversation, Label)
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

LABELING_SCHEMA = {
    'type': 'object',
    'required': ['label_id'],
    'properties': {
        'label_id': {'type': 'integer'}
    }
}


def get_account_thread(thread_id):
    """Get the thread with thread_id which belongs to current account."""
    try:
        return User.query(User).join(
            Platform, User.platform_id == Platform.id).filter(
                User.id == thread_id,
                Platform.account_id == g.account.id).one()
    except NoResultFound:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'No thread found')


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
    get_account_thread(thread_id)

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

    user = get_account_thread(thread_id)
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

    user = get_account_thread(thread_id)

    try:
        messaging.push_message(user, Message.FromDict(data['message']),
                               g.account_user.id)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHORIZED,
                       'Invalid message')
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/threads/<int:thread_id>/labels', methods=['GET'])
@login_required
def thread_list_labels(thread_id):
    """Add a label to thread."""
    user = get_account_thread(thread_id)
    return jsonify(labels=[label.to_json() for label in user.labels])


@app.route('/api/threads/<int:thread_id>/labels', methods=['POST'])
@login_required
def thread_add_label(thread_id):
    """Add a label to thread."""
    data = request.json
    try:
        jsonschema.validate(data, LABELING_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    label = Label.get_by(id=data['label_id'], account_id=g.account.id,
                         single=True)
    if not label:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'no matching label found')

    user = get_account_thread(thread_id)
    user.labels.append(label)

    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/threads/<int:thread_id>/labels', methods=['DELETE'])
@login_required
def thread_delete_label(thread_id):
    """Delete a label from thread."""
    data = request.json
    try:
        jsonschema.validate(data, LABELING_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    label = Label.get_by(id=data['label_id'], account_id=g.account.id,
                         single=True)
    if not label:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'no matching label found')

    user = get_account_thread(thread_id)
    try:
        user.labels.remove(label)
    except ValueError:
        DatabaseManager.rollback()
    else:
        DatabaseManager.commit()
    return jsonify(message='ok')
