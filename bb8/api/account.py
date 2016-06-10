# -*- coding: utf-8 -*-
"""
    handlers for accounts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import jsonify

from bb8 import app, AppError
from bb8.constant import HTTPStatus, CustomError
from bb8.api.forms import RegistrationForm, SocialRegistrationForm, LoginForm


@app.route('/email_register', methods=['POST'])
def email_register():
    form = RegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        return jsonify(message='ok')
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
def get_me():
    return jsonify(message='ok')
