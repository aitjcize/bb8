# -*- coding: utf-8 -*-
"""
    Common handler for requests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8 import app, config
from bb8.backend.database import DatabaseManager


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    DatabaseManager.connect()


@app.teardown_appcontext
def teardown_appcontext(unused_exc):
    """Closes the database at the end of the request."""
    DatabaseManager.disconnect(commit=config.COMMIT_ON_APP_TEARDOWN)
