# -*- coding: utf-8 -*-
"""
    Platform Format Parser
    ~~~~~~~~~~~~~~~~~~~~~~

    Parse a platform from *.platform file

    Copyright 2016 bb8 Authors
"""

import glob
import json
import os
import sys

import jsonschema

import bb8
from bb8 import logger
from bb8 import util
from bb8.backend.database import DatabaseManager, Platform


def get_platforms_dir():
    """Get directory contains platform definitions."""
    return os.path.join(bb8.SRC_ROOT, 'platforms')


def get_platform_filename(filename):
    """Get complete filename of bot file."""
    return os.path.join(get_platforms_dir(), filename)


def parse_platform(filename, to_platform_id=None):
    """Parse Platform from platform definition.

    If *to_platform_id* is specified, update existing platform specified by
    *to_platform_id* instead of creating a new platform.

    If *to_platform_id* is a callable. The result of the call is used as the
    platform_id.
    """
    schema = util.get_schema('platform')
    platform_json = None
    platform_json_text = None

    with open(filename, 'r') as f:
        try:
            platform_json_text = f.read()
            platform_json = json.loads(platform_json_text, encoding='utf8')
        except ValueError:
            raise RuntimeError('Invalid JSON file')

    try:
        jsonschema.validate(platform_json, schema)
    except jsonschema.exceptions.ValidationError:
        logger.exception('Validation failed for `%s\'!', filename)
        sys.exit(1)

    if callable(to_platform_id):
        to_platform_id = to_platform_id(platform_json)

    if to_platform_id:
        # Update existing platform.
        logger.info('Updating existing Platform(id=%d) with %s ...',
                    to_platform_id, filename)
        Platform.get_by(
            id=to_platform_id, return_query=True).update(platform_json)
    else:
        # Create a new platform.
        logger.info('Creating new platform from %s ...', filename)
        Platform(**platform_json).add()

    DatabaseManager.flush()


def build_all_platforms(include_dev=False):
    """Build all platforms from platform definitions."""
    for bot in glob.glob(get_platforms_dir() + '/*.platform'):
        parse_platform(bot)

    if include_dev:
        for bot in glob.glob(get_platforms_dir() + '/dev/*.platform'):
            parse_platform(bot)


def update_all_platforms():
    """Update all platforms from platform definitions."""
    def find_platform_by_name(platform_desc):
        platform = Platform.get_by(
            provider_ident=platform_desc['provider_ident'], single=True)
        if platform:
            return platform.id
        else:
            return None

    for platform in glob.glob(get_platforms_dir() + '/*.platform'):
        parse_platform(platform, find_platform_by_name)
