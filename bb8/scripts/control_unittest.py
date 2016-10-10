#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Deployment script unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import os
import unittest

import jsonschema

from bb8 import util
from bb8.scripts.control import BB8


class DeployUnittest(unittest.TestCase):
    def test_app_schema(self):
        schema = util.get_schema('app')
        for app_dir in BB8.get_app_dirs():
            with open(os.path.join(app_dir, 'manifest.json')) as f:
                manifest = json.load(f)

            jsonschema.validate(manifest, schema)


if __name__ == '__main__':
    unittest.main()
