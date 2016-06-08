# -*- coding: utf-8 -*-
"""
    bb8 Shell environment
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import inspect

import enum

from flask_script import Shell

from bb8 import app
from bb8.backend import database


def _make_context():
    """Initialize shell variables."""
    database.DatabaseManager.connect()
    env = {
        'DatabaseManager': database.DatabaseManager,
    }

    for obj_name in dir(database):
        obj = getattr(database, obj_name)
        if (inspect.isclass(obj) and
                (issubclass(obj, database.QueryHelperMixin) or
                 issubclass(obj, enum.Enum))):
            env[obj_name] = obj
    return dict(app=app, **env)


def install_commands(manager):
    """Install shell with customized make_context."""
    manager.add_command("shell", Shell(make_context=_make_context))
