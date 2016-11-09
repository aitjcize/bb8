# -*- coding: utf-8 -*-
"""
    handlers for accounts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import jsonschema
import pytz

from flask import g, jsonify, request

from bb8 import app
from bb8.constant import HTTPStatus, CustomError, Key
from bb8.api.error import AppError
from bb8.api.middlewares import login_required
from bb8.backend.database import Account, DatabaseManager


REGISTER_SCHEMA = {
    'type': 'object',
    'required': ['email', 'passwd', 'timezone'],
    'additionalProperties': False,
    'properties': {
        'email': {
            'type': 'string',
            'pattern': r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        },
        'passwd': {
            'type': 'string',
            'minLength': 6,
            'maxLength': 25
        },
        'timezone': {'type': 'string'}
    }
}

SOCIAL_REGISTER_SCHEMA = {
    'type': 'object',
    'required': ['provider', 'provider_ident'],
    'additionalProperties': False,
    'properties': {
        'provider': {'enum': ['Facebook', 'Google', 'Github']},
        'provider_ident': {'type': 'string'}
    }
}


@app.route('/api/email_register', methods=['POST'])
def email_register():
    data = request.json
    try:
        jsonschema.validate(data, REGISTER_SCHEMA)
        pytz.timezone(data['timezone'])
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    account = Account.get_by(email=data['email'], single=True)
    if not account:
        account = Account(email=data['email']).set_passwd(data['passwd']).add()
        DatabaseManager.commit()
    else:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_USER_EXISTED,
            'email %s is already taken' % data['email'])

    ret = account.to_json()
    ret[Key.AUTH_TOKEN] = account.auth_token
    return jsonify(ret)


@app.route('/api/social_register', methods=['POST'])
def social_register():
    data = request.json
    try:
        jsonschema.validate(data, SOCIAL_REGISTER_SCHEMA)
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    # TODO(aitjcize): implement this


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    account = Account.get_by(email=data['email'], single=True)
    if not account or not account.verify_passwd(data['passwd']):
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PASSWD,
                       'Invalid combination of email and password')

    ret = account.to_json()
    ret[Key.AUTH_TOKEN] = account.auth_token
    return jsonify(ret)


@app.route('/api/social_login', methods=['POST'])
def social_login():
    return jsonify(message='ok')


@app.route('/api/verify_email', methods=['GET'])
def verify_email():
    return jsonify(message='ok')


@app.route('/api/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(g.account.to_json())
