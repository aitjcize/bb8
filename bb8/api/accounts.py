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
from bb8.backend import oauth
from bb8.backend.account import register
from bb8.backend.database import AccountUser, DatabaseManager


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

SOCIAL_AUTH_SCHEMA = {
    'type': 'object',
    'required': ['email', 'provider', 'provider_token'],
    'additionalProperties': False,
    'properties': {
        'email': {
            'type': 'string',
            'pattern': r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        },
        'provider': {'enum': ['Facebook']},
        'provider_token': {'type': 'string'}
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

    account_user = AccountUser.get_by(email=data['email'], single=True)
    if not account_user:
        try:
            account_user = register(data, request.args.get('invite'))
        except RuntimeError as e:
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_BAD_INVITE_EMAIL,
                           str(e))
        DatabaseManager.commit()
    else:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_USER_EXISTED,
            'email %s is already taken' % data['email'])

    ret = account_user.to_json()
    ret[Key.AUTH_TOKEN] = account_user.auth_token
    return jsonify(ret)


@app.route('/api/social_auth', methods=['POST'])
def social_auth():
    data = request.json
    try:
        jsonschema.validate(data, SOCIAL_AUTH_SCHEMA)
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    try:
        facebook_id = oauth.facebook_verify_token(data['provider_token'])
    except Exception:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_UNAUTHENTICATED,
            'Invalid facebook token: %s' % data['provider_token'])

    try:
        account_user = AccountUser.register_oauth(
            data['email'], data['provider'], facebook_id,
            request.args.get('invite'))
    except Exception:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_WRONG_PARAM,
            'Cannot register the user')

    DatabaseManager.commit()

    ret = account_user.to_json()
    ret[Key.AUTH_TOKEN] = account_user.auth_token
    return jsonify(ret)


@app.route('/api/facebook_token_check', methods=['POST'])
def facebook_token_check():
    data = request.json

    try:
        oauth.facebook_verify_token(data['accessToken'])
    except Exception:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_UNAUTHENTICATED,
            'Invalid facebook token: %s' % data['accessToken'])

    return jsonify({'status': 'ok'})


@app.route('/api/facebook_token_extend', methods=['POST'])
def facebook_token_extend():
    data = request.json

    try:
        token = oauth.facebook_get_long_lived_token(data['accessToken'])
        return jsonify({'accessToken': token})
    except Exception:
        raise AppError(
            HTTPStatus.STATUS_CLIENT_ERROR,
            CustomError.ERR_UNAUTHENTICATED,
            'Failed to exchange token')


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    account = AccountUser.get_by(email=data['email'], single=True)
    if not account or not account.verify_passwd(data['passwd']):
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PASSWD,
                       'Invalid combination of email and password')

    ret = account.to_json()
    ret[Key.AUTH_TOKEN] = account.auth_token
    return jsonify(ret)


@app.route('/api/verify_email', methods=['GET'])
def verify_email():
    return jsonify(message='ok')


@app.route('/api/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(g.account_user.to_json())
