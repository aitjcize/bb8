# -*- coding: utf-8 -*-
"""
    Common handler for requests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8 import app, logger
from bb8.backend.database import DatabaseManager
from bb8.tracking import send_ga_track_info

# Register request handlers
from bb8.api import webhooks, third_party, misc  # pylint: disable=W0611


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    DatabaseManager.connect()


@app.teardown_appcontext
def teardown_appcontext(unused_exc):
    """Closes the database at the end of the request."""
    DatabaseManager.disconnect(commit=True)

    try:
        send_ga_track_info()
    except Exception as e:
        logger.exception(e)
