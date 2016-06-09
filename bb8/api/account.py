# -*- coding: utf-8 -*-
"""
    Handlers for
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import jsonify

from bb8 import app
from bb8 import AppError

@app.route('/email_register', methods=['POST'])
def email_register():
    return jsonify(message='ok')


@app.route('/social_register', methods=['POST'])
def social_register():
    return jsonify(message='ok')


@app.route('/login', methods=['POST'])
def login():
    return jsonify(message='ok')


@app.route('/social_login', methods=['POST'])
def social_login():
    return jsonify(message='ok')


@app.route('/verify_email', methods=['GET'])
def verify_email():
    return jsonify(message='ok')


@app.route('/me', methods=['GET'])
def get_me():
    return jsonify(message='ok')
