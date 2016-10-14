# -*- coding: utf-8 -*-
"""
    middlewares
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from functools import wraps

from flask import g, session

from bb8.api.error import AppError
from bb8.constant import HTTPStatus, CustomError, Key
from bb8.backend.database import Account


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if Key.ACCESS_TOKEN in session:
            token = session[Key.ACCESS_TOKEN]
            g.account = Account.from_auth_token(token)
            return func(*args, **kwargs)
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_UNAUTHENTICATED,
                       'Not loggined')
    return decorated
