# -*- coding: utf-8 -*-
"""
    Modules
    ~~~~~~~

    Modules management and registration.
    Iterate through all available module and register them.

    Copyright 2016 bb8 Authors
"""

from __future__ import print_function

import importlib
import json
import os
import re

from jsonschema import Draft4Validator

from bb8 import logger
from bb8.backend.database import DatabaseSession, ContentModule, ParserModule


def list_modules(module_dir, include_test=True):
    modules = []
    for root, unused_dirs, files in os.walk(module_dir):
        submodule_name = None
        if len(root) > len(module_dir):
            submodule_name = root[len(module_dir) + 1:].replace('/', '.')

        if not include_test and submodule_name == 'test':
            continue

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
            if not hasattr(m, 'get_module_info'):
                logger.warn('Skip module %s due to lack of get_module_info()' %
                            name)
                continue
            info = m.get_module_info()
            assert info['module_name'] == name

            try:
                Draft4Validator.check_schema(m.schema())
            except Exception:
                logger.error('module %s schema check failed', name)
                raise

            cm = ContentModule.get_by(id=info['id'], single=True)
            if cm:
                ContentModule.get_by(id=info['id'],
                                     return_query=True).update(info)
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
                ParserModule.get_by(id=info['id'],
                                    return_query=True).update(info)
            else:
                ParserModule(**info).add()


def register_all_modules():
    """Register all content and parser modules."""
    register_content_modules()
    register_parser_modules()


def compile_module_infos(filename=None):
    """Compile module schemas into a JSON file.

    The JSON file has the following format:

    export default ModuleInfo = {
        'content_modules': {
            'id': {
                // module info fields
                'schema': { // schema }
            },
            ...
        },
        'parser_modules': {
            'id': {
                // module info fields
                'schema': { // schema }
            },
            ...
        }
    }
    """
    module_info = {
        'content_modules': {},
        'parser_modules': {}
    }
    content_module_dir = os.path.join(os.path.dirname(__file__),
                                      'content_modules')
    parser_module_dir = os.path.join(os.path.dirname(__file__),
                                     'parser_modules')

    for name in list_modules(content_module_dir, include_test=False):
        m = importlib.import_module(
            '%s.%s' % (ContentModule.CONTENT_MODULES, name))
        if not hasattr(m, 'get_module_info'):
            continue
        info = m.get_module_info()
        info['supported_platform'] = info['supported_platform'].value
        info['schema'] = m.schema()
        module_info['content_modules'][info['id']] = info

    for name in list_modules(parser_module_dir, include_test=False):
        m = importlib.import_module(
            '%s.%s' % (ParserModule.PARSER_MODULES, name))
        if not hasattr(m, 'get_module_info'):
            continue
        info = m.get_module_info()
        info['supported_platform'] = info['supported_platform'].value
        info['schema'] = m.schema()
        module_info['parser_modules'][info['id']] = info

    json_content = json.dumps(module_info, indent=2)

    if filename is None:
        print(json_content)
    else:
        with open(filename, 'w') as f:
            f.write(json_content)
