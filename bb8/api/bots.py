# -*- coding: utf-8 -*-
"""
    Bot API Endpoint
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import jsonschema

from flask import g, jsonify, request

from bb8 import app, logger
from bb8.api.error import AppError
from bb8.constant import HTTPStatus, CustomError
from bb8.api.middlewares import login_required
from bb8.backend.database import Bot, BotDef, DatabaseManager
from bb8.backend.bot_parser import validate_bot_schema, parse_bot


BOT_CREATE_SCHEMA = {
    'type': 'object',
    'required': ['name', 'description'],
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'ga_id': {'type': 'string'},
    }
}


def get_account_bot_by_id(bot_id):
    bot = Bot.get_by(id=bot_id, account_id=g.account.id, single=True)
    if bot is None:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'bot_id: %d not found' % bot_id)
    return bot


@app.route('/api/bots', methods=['GET'])
@login_required
def list_bots():
    """List all bots."""
    return jsonify(bots=[b.to_json() for b in g.account.bots])


@app.route('/api/bots', methods=['POST'])
@login_required
def create_bot():
    """Create a new bot."""
    data = request.json
    try:
        jsonschema.validate(data, BOT_CREATE_SCHEMA)
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    bot = Bot(**data).add()
    g.account.bots.append(bot)
    DatabaseManager.commit()
    return jsonify(bot.to_json(bot.detail_fields))


@app.route('/api/bots/<int:bot_id>', methods=['GET'])
@login_required
def show_bot(bot_id):
    """Return Bot JSON object."""
    bot = get_account_bot_by_id(bot_id)
    return jsonify(bot.to_json(bot.detail_fields))


@app.route('/api/bots/<int:bot_id>', methods=['PATCH'])
@login_required
def update_bot(bot_id):
    """Only modify the name and description of the bot"""
    bot = get_account_bot_by_id(bot_id)
    try:
        jsonschema.validate(request.json['bot'], BOT_CREATE_SCHEMA)
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'The request json must contain'
                       ' name and description')

    bot.name = request.json['bot']['name']
    bot.description = request.json['bot']['description']
    bot.ga_id = request.json['bot']['ga_id']
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/bots/<int:bot_id>', methods=['PUT'])
@login_required
def deploy_bot(bot_id):
    bot = get_account_bot_by_id(bot_id)
    try:
        parse_bot(bot.staging, bot.id)
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Bot definition parsing failed')
    bot_def = BotDef.add_version(bot.id, bot.staging)
    bot.staging = None  # Clear staging area
    DatabaseManager.commit()
    return jsonify(version=bot_def.version)


@app.route('/api/bots/<int:bot_id>', methods=['DELETE'])
@login_required
def delete_bot(bot_id):
    bot = get_account_bot_by_id(bot_id)
    bot.delete()
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/bots/<int:bot_id>/revisions', methods=['PUT'])
@login_required
def update_bot_def_revisions(bot_id):
    """Modify bot staging area."""
    bot = get_account_bot_by_id(bot_id)
    try:
        validate_bot_schema(request.json)
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Bot definition parsing failed')

    bot.staging = request.json
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/bots/<int:bot_id>/revisions', methods=['GET'])
@login_required
def list_bot_def_revisions(bot_id):
    """List all available revision for a given bot."""
    bot = get_account_bot_by_id(bot_id)
    return jsonify(bot_defs=[d.to_json() for d in bot.bot_defs])


@app.route('/api/bots/<int:bot_id>/revisions/<int:version>', methods=['GET'])
@login_required
def get_bot_def_revision(bot_id, version):
    """Get bot_def JSON object given a version."""
    unused_bot = get_account_bot_by_id(bot_id)
    bot_def = BotDef.get_by(bot_id=bot_id, version=version, single=True)
    if bot_def is None:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'bot_def for bot_id %d, version %d not found' %
                       (bot_id, version))
    return jsonify(bot_def.to_json(['bot_json']))
