# -*- coding: utf-8 -*-
"""
    handlers for bots
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify

from bb8 import app, AppError
from bb8.constant import HTTPStatus, CustomError
from bb8.api.forms import CreateBotForm
from bb8.api.middlewares import login_required
from bb8.backend.database import Bot, DatabaseManager


@app.route('/bots', methods=['POST'])
@login_required
def create_bot():
    form = CreateBotForm(csrf_enabled=False)
    if form.validate_on_submit():
        bot = Bot(**form.data)
        g.account.bots.append(bot)
        DatabaseManager.commit()
        return jsonify(bot.to_json())
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION,
                   form.errors)


@app.route('/bots', methods=['GET'])
@login_required
def list_bots():
    return jsonify(bots=[b.to_json() for b in g.account.bots])


@app.route('/bots/<int:bot_id>', methods=['GET'])
@login_required
def show_bot(bot_id):
    bot = Bot.get_by(id=bot_id, single=True)
    if bot is None:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'bot id: %d not found' % bot_id)
    return jsonify(bot.to_json())


@app.route('/bots/<int:bot_id>', methods=['DELETE'])
@login_required
def delete_bot(bot_id):  # pylint: disable=W0613
    pass
