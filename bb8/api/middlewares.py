# -*- coding: utf-8 -*-
"""
    Middlewares
    ~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from functools import wraps

from flask import g, request

from bb8.api.error import AppError
from bb8.constant import HTTPStatus, CustomError, Key
from bb8.backend.database import Account


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if Key.X_COMPOSEAI_AUTH not in request.headers:
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_UNAUTHENTICATED,
                           'Not loggined')

        auth_header = request.headers[Key.X_COMPOSEAI_AUTH]
        parts = auth_header.split()
        if parts[0] != 'Bearer':
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_UNAUTHENTICATED,
                           'Invalid auth token')

        try:
            token = parts[1]
            g.account = Account.from_auth_token(token)
        except RuntimeError:
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_UNAUTHENTICATED,
                           'The token %s is invalid' % token)
        return func(*args, **kwargs)
    return decorated
