# -*- coding: utf-8 -*-
"""
    bb8 package level utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import os

from collections import OrderedDict

import jsonschema

import bb8
from bb8 import logger


def get_schema(name):
    """Get schema definition with *name* from bb8/schema directory."""
    filename = os.path.join(bb8.SRC_ROOT, 'schema', '%s.schema.json' % name)
    with open(filename, 'r') as f:
        schema_def = json.load(f, object_pairs_hook=OrderedDict)

    try:
        jsonschema.Draft4Validator.check_schema(schema_def)
    except Exception:
        logger.error('invalid schema found `%s\'', name)
        raise

    return schema_def
