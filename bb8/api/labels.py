# -*- coding: utf-8 -*-
"""
    Label API Endpoint
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g, jsonify, request

import jsonschema

from sqlalchemy.exc import IntegrityError

from bb8 import app
from bb8.api.error import AppError
from bb8.api.middlewares import login_required
from bb8.backend.database import DatabaseManager, Label
from bb8.constant import HTTPStatus, CustomError


LABEL_POST_SCHEMA = {
    'type': 'object',
    'required': ['name'],
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 32
        },
    }
}


@app.route('/api/labels', methods=['GET'])
@login_required
def list_label():
    """List all label owned by an account."""
    labels = Label.get_by(account_id=g.account.id)
    return jsonify(labels=[label.to_json() for label in labels])


@app.route('/api/labels', methods=['POST'])
@login_required
def post_label():
    """Add a new label for given account."""
    data = request.json
    try:
        jsonschema.validate(data, LABEL_POST_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    try:
        label = Label(account=g.account, name=data['name']).add()
        DatabaseManager.commit()
    except IntegrityError:
        DatabaseManager.rollback()
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_DUPLICATE_ENTRY,
                       'duplicate label')

    return jsonify(label.to_json())
