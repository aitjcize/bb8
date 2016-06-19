# -*- coding: utf-8 -*-
"""
    Common handler for requests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8 import app

from bb8.backend.database import DatabaseManager

# Register request handlers
from bb8.api import webhooks, third_party, misc  # pylint: disable=W0611


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    DatabaseManager.connect()


@app.after_request
def after_request(response):
    """Closes the database again at the end of the request."""
    DatabaseManager.disconnect()
    return response
