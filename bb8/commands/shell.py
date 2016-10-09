# -*- coding: utf-8 -*-
"""
    bb8 Shell environment
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from __future__ import print_function

import glob
import importlib
import inspect

import enum

from flask_script import Shell

from bb8 import app
from bb8.backend import database


def _make_context():
    class Namespace(object):
        pass

    """Initialize shell variables."""
    database.DatabaseManager.connect()
    env = {
        'DatabaseManager': database.DatabaseManager,
    }

    for database_file in glob.glob('./apps/*/*/database.py'):
        module_name = database_file.split('/')[-2]
        namespace = Namespace()

        database_path = module_name + '.database'
        print('Registering objects for %s ...' % database_path)

        db_module = importlib.import_module(database_path)
        db_module.DatabaseManager.connect()

        for obj_name in dir(db_module):
            obj = getattr(db_module, obj_name)
            if (inspect.isclass(obj) and
                    (issubclass(obj, db_module.ModelMixin) or
                     issubclass(obj, enum.Enum))):
                setattr(namespace, obj_name, obj)

        setattr(namespace,
                'DatabaseManager',
                db_module.DatabaseManager)
        env[module_name] = namespace

    for obj_name in dir(database):
        obj = getattr(database, obj_name)
        if (inspect.isclass(obj) and
                (issubclass(obj, database.ModelMixin) or
                 issubclass(obj, enum.Enum))):
            env[obj_name] = obj

    return dict(app=app, **env)


def install_commands(manager):
    """Install shell with customized make_context."""
    manager.add_command("shell", Shell(make_context=_make_context))
