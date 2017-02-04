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

import jsonschema

from sqlalchemy.exc import IntegrityError

import bb8
from bb8 import logger
from bb8.backend.database import (DatabaseManager, Bot, Platform,
                                  PlatformTypeEnum)
from bb8.backend.messaging import get_messaging_provider


class DuplicateEntryError(Exception):
    pass


def get_platforms_dir():
    """Get directory contains platform definitions."""
    return os.path.join(bb8.SRC_ROOT, 'platforms')


def get_platform_filename(filename):
    """Get complete filename of bot file."""
    return os.path.join(get_platforms_dir(), filename)


def validate_platform_schema(platform_json, source='platform_json'):
    try:
        jsonschema.validate(platform_json, Platform.schema())
    except jsonschema.exceptions.ValidationError:
        logger.error('Validation failed for `%s\'!', source)
        raise


def parse_platform(platform_json, to_platform_id=None, source='platform_json'):
    """Parse Platform from platform definition.

    If *to_platform_id* is specified, update existing platform specified by
    *to_platform_id* instead of creating a new platform.

    If *to_platform_id* is a callable. The result of the call is used as the
    platform_id.
    """
    validate_platform_schema(platform_json)

    # Validate plaform-specific schema
    provider = get_messaging_provider(
        PlatformTypeEnum(platform_json['type_enum']))
    try:
        jsonschema.validate(platform_json['config'],
                            provider.get_config_schema())
    except jsonschema.exceptions.ValidationError:
        logger.error('Platform config validate failed for `%s\'!', source)
        raise

    if callable(to_platform_id):
        to_platform_id = to_platform_id(platform_json)

    bot_id = platform_json.get('bot_id')
    if bot_id:
        bot = Bot.get_by(id=bot_id, account_id=platform_json['account_id'],
                         single=True)
        if not bot:
            raise RuntimeError('bot does not exist')

    if to_platform_id:
        # Update existing platform.
        logger.info(u'Updating existing Platform(id=%d, name=%s) from %s ...',
                    to_platform_id, platform_json['name'], source)
        platform = Platform.get_by(id=to_platform_id, single=True)
        platform.bot_id = bot_id
        platform.name = platform_json['name']
        platform.deployed = platform_json['deployed']
        platform.type_enum = platform_json['type_enum']
        platform.provider_ident = platform_json['provider_ident']
        platform.config = platform_json['config']
    else:
        # Create a new platform.
        logger.info(u'Creating new Platform(name=%s) from %s ...',
                    platform_json['name'], source)
        platform = Platform(**platform_json).add()

    try:
        DatabaseManager.commit()
    except IntegrityError:
        DatabaseManager.rollback()
        raise DuplicateEntryError()

    # Invalidate Platform cache.
    platform.invalidate_cached()

    return platform


def parse_platform_from_file(filename, to_platform_id=None):
    with open(filename, 'r') as f:
        try:
            platform_json = json.load(f, encoding='utf8')
        except ValueError:
            raise RuntimeError('Invalid JSON file')

    return parse_platform(platform_json, to_platform_id, filename)


def build_all_platforms(include_dev=False):
    """Build all platforms from platform definitions."""
    for platform in glob.glob(get_platforms_dir() + '/*.platform'):
        parse_platform_from_file(platform)

    if include_dev:
        for bot in glob.glob(get_platforms_dir() + '/dev/*.platform'):
            parse_platform_from_file(bot)


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
        parse_platform_from_file(platform, find_platform_by_name)
