# -*- coding: utf-8 -*-
"""
    bb8 Test Server Runner
    ~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from flask_script import Server

from bb8 import config


# pylint: disable=W0223
class TestServer(Server):
    def __init__(self, *unused_args, **unused_kwargs):
        bb8_root = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                 '..', '..'))
        context = (
            os.path.join(bb8_root, 'certs/cert.pem'),
            os.path.join(bb8_root, 'certs/key.pem')
        )

        super(TestServer, self).__init__(
            host='0.0.0.0', port=config.HTTP_PORT, ssl_context=context)

    def __call__(self, *args, **kwargs):
        super(TestServer, self).__call__(*args, **kwargs)


def install_commands(manager):
    manager.add_command('runserver', TestServer())
