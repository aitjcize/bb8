# -*- coding: utf-8 -*-
"""
    Payment
    ~~~~~~~

    Payment related operations.

    Copyright 2016 bb8 Authors
"""

import jsonschema

from flask import jsonify, request

from bb8 import app, config
from bb8.api.error import AppError
from bb8.api.middlewares import login_required
from bb8.backend import payment
from bb8.backend.database import DatabaseManager
from bb8.constant import HTTPStatus, CustomError


PAYMENT_UPDATE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'token': {'type': 'string'},
        'subscription': {
            'type': 'object',
            'required': ['plan', 'action'],
            'properties': {
                'plan': {'enum': ['basic-monthly']},
                'action': {'enum': ['Start', 'Stop']}
            }
        }
    }
}


@app.route('/payment', methods=['POST'])
def stripe_webhook():
    auth = request.headers.get('Authorization')
    if not auth:
        raise AppError(HTTPStatus.STATUS_UNAUTHORIZED,
                       CustomError.ERR_UNAUTHORIZED,
                       'bad authorization')

    if auth != 'Basic %s' % config.STRIPE_WEBHOOK_CREDENTIAL:
        raise AppError(HTTPStatus.STATUS_UNAUTHORIZED,
                       CustomError.ERR_UNAUTHORIZED,
                       'bad authorization')

    event = request.json

    if event['type'] == 'invoice.payment_succeeded':
        payment.process_successful_payment_event(event)
    elif event['type'] == 'invoice.payment_failed':
        payment.process_failed_payment_event(event)
    elif event['type'] == 'customer.subscription.trial_will_end':
        payment.process_trial_will_end_event(event)

    DatabaseManager.commit()
    return 'ok'


@app.route('/api/payment/update', methods=['PATCH'])
@login_required
def update_payment():
    data = request.json
    try:
        jsonschema.validate(data, PAYMENT_UPDATE_SCHEMA)
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_FORM_VALIDATION,
                       'schema validation fail')

    try:
        payment.update_payment(data)
        DatabaseManager.commit()
    except payment.InvalidSourceTokenError:
        DatabaseManager.rollback()
        raise AppError(HTTPStatus.STATUS_SERVER_ERROR,
                       CustomError.ERR_INVALID_STRIPE_TOKEN,
                       'invalid stripe token')
    except Exception as e:
        DatabaseManager.rollback()
        raise AppError(HTTPStatus.STATUS_SERVER_ERROR,
                       CustomError.ERR_UNKNOWN_ERROR,
                       str(e))
    return jsonify(message='ok')
