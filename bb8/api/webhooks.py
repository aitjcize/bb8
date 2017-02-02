# -*- coding: utf-8 -*-
"""
    Chatbot webhooks
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import hashlib
import hmac

from flask import request

from bb8 import app, config, logger
from bb8.api.error import AppError
from bb8.backend.database import Platform
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.webhooks_tasks import facebook_webhook_task, line_webhook_task


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['GET'])
def facebook_challenge():
    """Facebook Bot API challenge."""
    if (request.args['hub.verify_token'] ==
            config.FACEBOOK_WEBHOOK_VALIDATION_TOKEN):
        return request.args['hub.challenge']
    return 'Error, wrong validation token'


@app.route(config.FACEBOOK_WEBHOOK_PATH, methods=['POST'])
def facebook_receive():
    """Facebook Bot API receive."""
    # Only verify signature in production environment
    if config.DEPLOY:
        digest = hmac.new(config.FACEBOOK_APP_SECRET,
                          request.data.decode('utf-8'),
                          hashlib.sha1).hexdigest()
        signature = 'sha1=%s' % digest

        if signature != request.headers['X-Hub-Signature']:
            raise AppError(HTTPStatus.STATUS_UNAUTHORIZED,
                           CustomError.ERR_UNAUTHORIZED,
                           'failed to verify message')
    try:
        if config.DEPLOY:
            facebook_webhook_task.apply_async(priority=9)
        else:
            facebook_webhook_task()
    except Exception as e:
        logger.exception(e)
    return 'ok'


@app.route(config.LINE_WEBHOOK_PATH, methods=['POST'])
def line_receive(provider_ident):
    """LINE Bot API receive."""
    platform = Platform.get_cached(provider_ident)
    if platform is None:
        raise AppError(HTTPStatus.STATUS_NOT_FOUND,
                       CustomError.ERR_NOT_FOUND,
                       'no associate bot found for Line Platform with '
                       'ident = %s' % provider_ident)

    digest = hmac.new(str(platform.config['channel_secret']),
                      request.data, hashlib.sha256).digest()
    signature = base64.b64encode(digest)

    if signature != request.headers['X-Line-Signature']:
        raise AppError(HTTPStatus.STATUS_UNAUTHORIZED,
                       CustomError.ERR_UNAUTHORIZED,
                       'failed to verify message')
    try:
        if config.DEPLOY:
            line_webhook_task.apply_async((provider_ident,), priority=9)
        else:
            line_webhook_task(provider_ident)
    except Exception as e:
        logger.exception(e)
    return 'ok'
