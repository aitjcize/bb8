# -*- coding: utf-8 -*-
"""
    Module Registration
    ~~~~~~~~~~~~~~~~~~~

    Iterate through all available module and register them.

    Copyright 2016 bb8 Authors
"""

import importlib
import os
import re

from jsonschema import Draft4Validator

from bb8 import logger
from bb8.backend.database import DatabaseSession, ContentModule, ParserModule


def list_modules(module_dir):
    modules = []
    for root, unused_dirs, files in os.walk(module_dir):
        submodule_name = None
        if len(root) > len(module_dir):
            submodule_name = root[len(module_dir) + 1:].replace('/', '.')

        for f in files:
            if (f.endswith('.py') and not
                    f.startswith('_') and not
                    f.endswith('unittest.py')):
                f = re.sub(r'\.py$', '', f)
                if submodule_name:
                    modules.append('%s.%s' % (submodule_name, f))
                else:
                    modules.append(f)
    return modules


def register_content_modules():
    """List all content modules and register them in the database."""
    module_dir = os.path.join(os.path.dirname(__file__), 'content_modules')
    modules = list_modules(module_dir)

    with DatabaseSession(disconnect=False):
        for name in modules:
            logger.info('Registering content module `%s\' ...', name)
            m = importlib.import_module('%s.%s' %
                                        (ContentModule.CONTENT_MODULES, name))
            info = m.get_module_info()
            assert info['module_name'] == name

            try:
                Draft4Validator.check_schema(m.schema())
            except Exception:
                logger.error('module %s schema check failed', name)
                raise

            cm = ContentModule.get_by(id=info['id'], single=True)
            if cm:
                ContentModule.get_by(id=info['id'], query=True).update(info)
            else:
                ContentModule(**info).add()


def register_parser_modules():
    """List all parser modules and register them in the database."""
    module_dir = os.path.join(os.path.dirname(__file__), 'parser_modules')
    modules = list_modules(module_dir)

    with DatabaseSession(disconnect=False):
        for name in modules:
            logger.info('Registering parser module `%s\' ...', name)
            m = importlib.import_module('%s.%s' %
                                        (ParserModule.PARSER_MODULES, name))
            info = m.get_module_info()
            assert info['module_name'] == name

            try:
                Draft4Validator.check_schema(m.schema())
            except Exception:
                logger.error('module %s schema check failed', name)
                raise

            pm = ParserModule.get_by(id=info['id'], single=True)
            if pm:
                ParserModule.get_by(id=info['id'], query=True).update(info)
            else:
                ParserModule(**info).add()


def register_all_modules():
    """Register all content and parser modules."""
    register_content_modules()
    register_parser_modules()
