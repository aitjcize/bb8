# -*- coding: utf-8 -*-
"""
    handlers for accounts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify

from bb8 import app, AppError
from bb8.constant import HTTPStatus, CustomError, Key
from bb8.api.forms import RegistrationForm, SocialRegistrationForm, LoginForm
from bb8.api.middlewares import login_required
from bb8.backend.database import Account, DatabaseManager


@app.route('/api/email_register', methods=['POST'])
def email_register():
    form = RegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_info = {
            'username': form.data['username'],
            'email': form.data['email'],
        }
        account = Account.get_by(email=form.data['email'], single=True)
        if not account:
            account = Account(**user_info) \
                        .set_passwd(form.data['passwd']) \
                        .add()
            DatabaseManager.commit()
        else:
            raise AppError(
                HTTPStatus.STATUS_CLIENT_ERROR,
                CustomError.ERR_USER_EXISTED,
                'username {username} or email {email} is already taken'
                .format(**user_info))

        ret = account.to_json()
        ret[Key.AUTH_TOKEN] = account.auth_token
        return jsonify(ret)

    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


@app.route('/api/social_register', methods=['POST'])
def social_register():
    form = SocialRegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        return jsonify(message='ok')
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


@app.route('/api/login', methods=['POST'])
def login():
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        email = form.data['email']
        passwd = form.data['passwd']
        account = Account.get_by(email=email, single=True)
        if not account or not account.verify_passwd(passwd):
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_WRONG_PASSWD,
                           'Invalid combination of email and password')

        ret = account.to_json()
        ret[Key.AUTH_TOKEN] = account.auth_token
        return jsonify(ret)
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


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
