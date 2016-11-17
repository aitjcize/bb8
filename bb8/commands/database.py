# -*- coding: utf-8 -*-
"""
    bb8 Database Managemnt
    ~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask_script import Command

from bb8.backend import bot_parser
from bb8.backend import modules
from bb8.backend import platform_parser
from bb8.backend.database import DatabaseManager, DatabaseSession


class ResetCommand(Command):
    """Reset database and populate with modules and bots"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            DatabaseManager.reset()
            modules.register_all()
            platform_parser.build_all_platforms()
            bot_parser.build_all_bots()


class ResetForDevCommand(Command):
    """Reset database and populate with modules and bots (dev environment)"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            DatabaseManager.reset()
            modules.register_all()
            platform_parser.build_all_platforms(include_dev=True)
            bot_parser.build_all_bots()


class RegisterModulesCommand(Command):
    """Register all bot modules"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            modules.register_all()


class GeneratePlatformsCommand(Command):
    """Generate all platforms from bot definitions"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            platform_parser.build_all_platforms()


class UpdatePlatformsCommand(Command):
    """Update and generate all platforms from platform definitions"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            platform_parser.update_all_platforms()


class GenerateBotsCommand(Command):
    """Generate all bots from bot definitions"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            bot_parser.build_all_bots()


class UpdateBotsCommand(Command):
    """Update and generate all bots from bot definitions"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            bot_parser.update_all_bots()


commands = {
    'reset': ResetCommand,
    'reset_for_dev': ResetForDevCommand,
    'register_modules': RegisterModulesCommand,
    'generate_platforms': GeneratePlatformsCommand,
    'update_platforms': UpdatePlatformsCommand,
    'generate_bots': GenerateBotsCommand,
    'update_bots': UpdateBotsCommand
}


def install_commands(manager):
    for name, command in commands.items():
        manager.add_command(name, command())
