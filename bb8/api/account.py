# -*- coding: utf-8 -*-
"""
    handlers for accounts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import jsonify, session

from bb8 import app, AppError
from bb8.constant import HTTPStatus, CustomError, Key
from bb8.api.forms import RegistrationForm, SocialRegistrationForm, LoginForm
from bb8.api.middlewares import login_required
from bb8.backend.database import Account


@app.route('/email_register', methods=['POST'])
def email_register():
    form = RegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_info = {
            'username': form.data['username'],
            'email': form.data['email'],
        }
        account = Account.get_by(single=True, **user_info)
        if not account:
            account = Account(**user_info) \
                        .set_passwd(form.data['passwd']) \
                        .add()
            Account.commit()
        else:
            raise AppError(
                HTTPStatus.STATUS_CLIENT_ERROR,
                CustomError.ERR_USER_EXISTED,
                "username {username} or email {email} is already taken"
                .format(**user_info))

        session[Key.ACCESS_TOKEN] = account.auth_token

        # TODO: Send a email confirmation
        return jsonify(account.to_json())
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


@app.route('/social_register', methods=['POST'])
def social_register():
    form = SocialRegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        return jsonify(message='ok')
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        account = Account.get_by(id=1, single=True)
        session[Key.ACCESS_TOKEN] = account.auth_token
        return jsonify(message='ok')
    raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                   CustomError.ERR_FORM_VALIDATION, form.errors)


@app.route('/social_login', methods=['POST'])
def social_login():
    return jsonify(message='ok')


@app.route('/verify_email', methods=['GET'])
def verify_email():
    return jsonify(message='ok')


@app.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(message='ok')
