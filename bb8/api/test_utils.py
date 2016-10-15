# -*- coding: utf-8 -*-
"""
    API Test utils
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask.testing import FlaskClient

from bb8.constant import Key


class BearerAuthTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self._auth_token = None
        super(BearerAuthTestClient, self).__init__(*args, **kwargs)

    def set_auth_token(self, token):
        self._auth_token = token

    def _add_auth_header(self, kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'][Key.X_COMPOSEAI_AUTH] = ('Bearer %s' %
                                                   self._auth_token)

    def open(self, *args, **kwargs):
        self._add_auth_header(kwargs)
        return super(BearerAuthTestClient, self).open(*args, **kwargs)
