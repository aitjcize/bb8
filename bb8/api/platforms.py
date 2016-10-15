# -*- coding: utf-8 -*-
"""
    Platform API Endpoint
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify, request

from bb8 import app, logger, AppError
from bb8.constant import HTTPStatus, CustomError
from bb8.api.middlewares import login_required
from bb8.backend.database import DatabaseManager, Platform
from bb8.backend.platform_parser import parse_platform


def get_account_platform_by_id(platform_id):
    platform = Platform.get_by(id=platform_id, account_id=g.account.id,
                               single=True)
    if platform is None:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_NOT_FOUND,
                       'platform_id: %d not found' % platform_id)
    return platform


@app.route('/api/platforms', methods=['GET'])
@login_required
def list_platforms():
    """List all platforms."""
    return jsonify(platforms=[p.to_json() for p in g.account.platforms])


@app.route('/api/platforms', methods=['POST'])
@login_required
def create_platform():
    """Create a new platform."""
    try:
        platform_json = request.json
        platform_json['account_id'] = g.account.id
        platform = parse_platform(platform_json)
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Platform definition parsing failed')
    DatabaseManager.commit()
    return jsonify(platform.to_json(['config']))


@app.route('/api/platforms/<int:platform_id>', methods=['GET'])
@login_required
def show_platform(platform_id):
    platform = get_account_platform_by_id(platform_id)
    return jsonify(platform.to_json(['config']))


@app.route('/api/platforms/<int:platform_id>', methods=['PUT'])
@login_required
def update_platform(platform_id):
    """Update a platform."""
    platform = get_account_platform_by_id(platform_id)
    try:
        platform_json = request.json
        platform_json['account_id'] = g.account.id
        platform = parse_platform(platform_json, platform.id)
    except Exception as e:
        logger.exception(e)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Platform definition parsing failed')
    DatabaseManager.commit()
    return jsonify(message='ok')


@app.route('/api/platforms/<int:platform_id>', methods=['DELETE'])
@login_required
def delete_platform(platform_id):
    """Delete a platform."""
    platform = get_account_platform_by_id(platform_id)
    platform.delete()
    DatabaseManager.commit()
    return jsonify(message='ok')
