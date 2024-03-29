# -*- coding: utf-8 -*-
"""
    Engine for executing logic graph
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import random
import re

from flask import g

from bb8 import logger
from bb8.backend import messaging
from bb8.backend.message import Message, Render
from bb8.tracking import track, TrackingInfo
from bb8.backend.database import (Bot, DatabaseManager, Node,
                                  SupportedPlatform, ModuleTypeEnum)
from bb8.backend.metadata import RouteResult
from bb8.backend.message import InputTransformation


HAS_VARIABLE_RE = re.compile('{{(.*?)}}')


class Engine(object):
    STEP_MAX_DEPTH = 30

    def send_ack_message(self, user, message, variables):
        """Send text message.

        If *messages* is a list of message, choice a random one from the
        list then send it.
        """
        if isinstance(message, list):
            message = random.choice(message)

        messaging.send_message(user, Message(message, variables=variables))

    def run(self, bot, user, user_input=None, input_vars=None):
        """Main function for executing a node."""

        try:  # pylint: disable=R0101
            now = datetime.datetime.now()

            if user.session is None:
                if user_input:
                    user_input.disable_jump()
                user.goto(Bot.START_STABLE_ID)

            g.user = user
            if user_input:
                # Parse audio as text if there are audio payload
                user_input.ParseAudioAsText(user)
                user_input = user_input.RunInputTransformation()

            # If there was admin interaction, and admin_interaction_timeout
            # haven't reached yet, do not run engine.
            if (bot.admin_interaction_timeout > 0 and
                    ((now - user.last_admin_seen).total_seconds() <
                     bot.admin_interaction_timeout)):
                return

            # Check has been idle for too long, reset it's state if yes.
            if (bot.session_timeout > 0 and
                    ((now - user.last_seen).total_seconds() >
                     bot.session_timeout)):
                user.last_seen = datetime.datetime.now()
                user.goto(Bot.ROOT_STABLE_ID)

            if user_input and user_input.jump():
                node = Node.get_cached(bot.id, user_input.jump_node_id)
                # Check if the node belongs to current bot
                if node is None:
                    logger.critical('Invalid jump node_id %s' %
                                    user_input.jump_node_id)
                # If payload button is pressed, we need to jump to the
                # corresponding node if payload's node_id != current_node_id
                elif user_input.jump_node_id != user.session.node_id:
                    user.goto(user_input.jump_node_id)

            self.step(bot, user, user_input, input_vars)

            messaging.flush_message(user)
        except Exception as e:
            logger.exception(e)
            # Rollback when error happens, so user won't get stuck in some
            # weird state.
            DatabaseManager.rollback()
        finally:
            user.last_seen = datetime.datetime.now()
            DatabaseManager.commit()

    def run_router_module(self, node, user_input, init_variables,
                          as_root=False):
        """Execute a parser module of a node, then return end_node_id."""
        module = node.module.get_python_module()
        result = module.run(node.config, user_input, as_root)
        assert isinstance(result, RouteResult)

        variables = result.variables
        variables.update(init_variables)
        return result, variables

    def step(self, bot, user, user_input=None, input_vars=None, depth=0):
        # Don't do anything if STEP_MAX_DEPTH reached
        if depth > Engine.STEP_MAX_DEPTH:
            logger.critical('STEP_MAX_DEPTH is reached!')
            return

        node = Node.get_cached(bot.id, user.session.node_id)
        g.node = node

        if node is None:
            logger.critical('Invalid node_id %s' % user.session.node_id)
            user.goto(Bot.ROOT_STABLE_ID)
            return self.step(bot, user, user_input, depth=depth + 1)

        if user_input is None and node.expect_input:
            return

        track(TrackingInfo.Pageview(user.platform_user_ident,
                                    '/%s' % node.stable_id))

        # Shared global variables
        global_variables = {
            'user': user.to_json(),
            'bot_id': bot.id
        }

        if node.module.type != ModuleTypeEnum.Router:
            env = {
                'platform_type': SupportedPlatform(
                    user.platform.type_enum.value)
            }
            # Prepare input variables
            input_vars = input_vars or {}
            input_vars.update(global_variables)

            # Clear input transformation for a new content module.
            if node.module.type == ModuleTypeEnum.Content:
                user.session.input_transformation = []

            # TODO(aitjcize): figure out how to deal with module exceptions
            module = node.module.get_python_module()
            result = module.run(node.config, user_input, env, input_vars)

            for k, v in result.memory.iteritems():
                user.memory[k] = v

            # Send message
            if result.messages:
                messaging.send_message(user, result.messages)

                # Store InputTransformation in session
                user.session.input_transformation = InputTransformation.get()

            next_node_id = node.next_node_id
            if next_node_id and re.search(HAS_VARIABLE_RE, next_node_id):
                next_node_id = Render(next_node_id, {})

            # Goto the next node
            user.goto(next_node_id if next_node_id else Bot.ROOT_STABLE_ID)

            # Content modules 'consumes' users input, so don't pass it to the
            # next step.
            if node.module.type == ModuleTypeEnum.Content:
                user_input = None

            return self.step(bot, user, user_input,
                             dict(input_vars, **result.variables),
                             depth=depth + 1)
        elif node.module.type == ModuleTypeEnum.Router:
            result, variables = self.run_router_module(
                node, user_input, global_variables, False)

            # Node router failed, try root router:
            if result.errored and node.stable_id != Bot.ROOT_STABLE_ID:
                root_result, root_variables = self.run_router_module(
                    bot.node(Bot.ROOT_ROUTER_STABLE_ID), user_input,
                    global_variables, True)

                # If root paser matched, use root_parser result as result.
                if not root_result.errored:
                    result = root_result
                    variables = root_variables

            if result.ack_message:
                self.send_ack_message(user, result.ack_message, variables)

            if user.session.node_id == result.end_node_id:
                # We are going back to the same node, clear user-input to
                # avoid infinite loop.
                user_input = None
            else:
                # Goto the next node
                user.goto(result.end_node_id if result.end_node_id else
                          Bot.ROOT_STABLE_ID)

            # Run next module
            return self.step(bot, user, user_input, variables, depth=depth + 1)

    def process_admin_reply(self, bot, user, unused_user_input=None,
                            unused_input_vars=None):
        try:
            if bot.admin_interaction_timeout > 0:
                user.last_admin_seen = datetime.datetime.now()
        finally:
            DatabaseManager.commit()
