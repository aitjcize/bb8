# -*- coding: utf-8 -*-
"""
    bb8 Databse Managemnt
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask_script import Command

from bb8.backend.bot_parser import build_all_bots, update_all_bots
from bb8.backend.database import DatabaseManager, DatabaseSession
from bb8.backend.module_registration import register_all_modules


class ResetCommand(Command):
    """Reset database and populate with modules and bots"""
    def run(self):  # pylint: disable=E0202
        with DatabaseSession():
            DatabaseManager.reset()
        register_all_modules()
        build_all_bots()


class RegisterModulesCommand(Command):
    """Register all bot modules"""
    def run(self):  # pylint: disable=E0202
        register_all_modules()


class GenerateBotsCommand(Command):
    """Generate all bots from bot definitions"""
    def run(self):  # pylint: disable=E0202
        build_all_bots()


class UpdateBotsCommand(Command):
    """Update and generate all bots from bot definitions"""
    def run(self):  # pylint: disable=E0202
        update_all_bots()


commands = {
    'reset': ResetCommand,
    'register_modules': RegisterModulesCommand,
    'generate_bots': GenerateBotsCommand,
    'update_bots': UpdateBotsCommand
}


def install_commands(manager):
    for name, command in commands.items():
        manager.add_command(name, command())
