# -*- coding: utf-8 -*-
"""
    Content API Endpoint
    ~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify, request

from bb8 import app, AppError
from bb8.constant import HTTPStatus, CustomError
from bb8.api.middlewares import login_required
from bb8.api.forms import CreateFeedForm
from bb8.api.util import validate_uint
from bb8.backend.database import DatabaseManager, Feed


@app.route('/api/public_feeds', methods=['GET'])
@login_required
def search_public_feeds():
    search = request.args.get('search', '')
    if search == '':
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'search should not be empty string')
    return Feed.search_title(search)


@app.route('/api/feeds', methods=['POST'])
@login_required
def create_feed():
    form = CreateFeedForm(csrf_enabled=False)
    if form.validate_on_submit():
        feed = Feed(**form.data).add()
        g.account.feeds.append(feed)
        DatabaseManager.commit()
        return jsonify(feed=feed.to_json())
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION,
                   form.errors)


@app.route('/api/feeds', methods=['GET'])
@login_required
def get_feeds():
    limit = validate_uint(request.args.get('limit', 10), 0, 50, 10)
    offset = validate_uint(request.args.get('offset', 0), 0, -1, 0)

    feeds = g.account.feeds.limit(limit).offset(offset).all()
    return jsonify(feeds=[f.to_json() for f in feeds])


@app.route('/api/feeds/<int:feed_id>', methods=['GET'])
@login_required
def list_feed_entries(feed_id):  # pylint: disable=W0613
    return jsonify(g.account.to_json())


@app.route('/api/feeds/<int:feed_id>', methods=['PATCH'])
@login_required
def update_feed(feed_id):  # pylint: disable=W0613
    return jsonify(g.account.to_json())


@app.route('/api/feeds/<int:feed_id>', methods=['DELETE'])
@login_required
def delete_feed(feed_id):  # pylint: disable=W0613
    return jsonify(g.account.to_json())


@app.route('/api/entries/', methods=['POST'])
@login_required
def create_entry():
    return jsonify(g.account.to_json())


@app.route('/api/entries/', methods=['GET'])
@login_required
def get_entries():
    return jsonify(g.account.to_json())


@app.route('/api/entries/<int:entry_id>', methods=['PATCH'])
@login_required
def updae_entry(entry_id):  # pylint: disable=W0613
    return jsonify(g.account.to_json())


@app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):  # pylint: disable=W0613
    return jsonify(g.account.to_json())