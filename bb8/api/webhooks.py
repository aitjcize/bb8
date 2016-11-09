# -*- coding: utf-8 -*-
"""
    Chatbot webhooks
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import request

from bb8 import app, config, logger
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
    try:
        if config.DEPLOY:
            facebook_webhook_task.apply_async()
        else:
            facebook_webhook_task()
    except Exception as e:
        logger.exception(e)
    return 'ok'


@app.route(config.LINE_WEBHOOK_PATH, methods=['POST'])
def line_receive(provider_ident):
    """LINE Bot API receive."""
    try:
        if config.DEPLOY:
            line_webhook_task.apply_async((provider_ident,))
        else:
            line_webhook_task(provider_ident)
    except Exception as e:
        logger.exception(e)
    return 'ok'
