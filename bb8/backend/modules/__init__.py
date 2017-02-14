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
from bb8.backend.database import DatabaseSession, Module


def list_all_modules():
    module_dir = os.path.dirname(__file__)
    return list_modules(module_dir, include_test=False)


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


def register_all():
    """List all modules and register them in the database."""
    module_dir = os.path.dirname(__file__)
    modules = list_modules(module_dir)

    with DatabaseSession(disconnect=False):
        for name in modules:
            logger.info('Registering module `%s\' ...', name)
            m = importlib.import_module('%s.%s' %
                                        (Module.MODULE_PACKAGE, name))
            if not hasattr(m, 'properties'):
                logger.warn('Skip module %s due to lack of properties()' %
                            name)
                continue

            info = m.properties()
            info['module_name'] = name

            try:
                Draft4Validator.check_schema(m.schema())
            except Exception:
                logger.error('module %s schema check failed', name)
                raise

            m = Module.get_by(id=info['id'], single=True)
            if m:
                Module.get_by(id=info['id'], return_query=True).update(info)
            else:
                Module(**info).add()


def compile_module_infos(filename=None):
    """Compile module schemas into a JSON file.

    The JSON file has the following format:

    export default ModuleInfo = {
        'id': {
            // module info fields
            'schema': { // schema }
        },
        ...
    }
    """
    module_info = {}
    module_dir = os.path.dirname(__file__)

    for name in list_modules(module_dir, include_test=False):
        m = importlib.import_module(
            '%s.%s' % (Module.MODULE_PACKAGE, name))
        if not hasattr(m, 'properties'):
            continue
        info = m.properties()
        info['type'] = info['type'].value
        info['supported_platform'] = info['supported_platform'].value
        info['schema'] = m.schema()
        module_info[info['id']] = info

    json_content = json.dumps(module_info, indent=2)

    if filename is None:
        print(json_content)
    else:
        with open(filename, 'w') as f:
            f.write(json_content)
