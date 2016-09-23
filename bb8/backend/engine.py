# -*- coding: utf-8 -*-
"""
    Engine for executing logic graph
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import random

from flask import g

from bb8 import config, logger
from bb8.backend import messaging
from bb8.tracking import track, TrackingInfo
from bb8.backend.database import (DatabaseManager, Conversation, ColletedDatum,
                                  Linkage, Node, SupportedPlatform, SenderEnum,
                                  User)
from bb8.backend.metadata import ParseResult, InputTransformation


class Engine(object):
    BB8_GLOBAL_NOMATCH_IDENT = '$bb8.global.nomatch'

    def __init__(self):
        pass

    def send_ack_message(self, user, message, variables):
        """Send text message.

        If *messages* is a list of message, choice a random one from the
        list then send it.
        """
        if isinstance(message, list):
            message = random.choice(message)

        messaging.send_message(
            user, messaging.Message(message, variables=variables))

    def insert_data(self, user, data):
        """Insert collected data into database."""
        for key in data:
            ColletedDatum(user_id=user.id, key=key, value=data[key]).add()

    def run_parser_module(self, node, user, user_input, init_variables,
                          as_root=False):
        """Execute a parser module of a node, then return linkage.

        If action_ident is BB8_GLOBAL_NOMATCH_IDENT (should only happen in case
        of running root parser modele (global command). Return without
        attempting to find a linkage.
        """
        pm = node.parser_module.get_module()
        result = pm.run(node.parser_config, user_input, as_root)
        assert isinstance(result, ParseResult)

        variables = result.variables
        variables.update(init_variables)

        # Parser module can optionally send a message directly back to user.
        if result.ack_message:
            self.send_ack_message(user, result.ack_message, variables)

        # Global parser nomatch
        if not result.matched:
            return result, None, init_variables

        # Collect data
        if result.collected_datum:
            self.insert_data(user, result.collected_datum)

        # Track error
        if result.action_ident == '$error':
            track(TrackingInfo.Event(user.platform_user_ident,
                                     'Parser', 'Error', user_input.text))

        linkage = Linkage.get_by(start_node_id=node.id,
                                 action_ident=result.action_ident, single=True)
        if linkage and linkage.ack_message:
            self.send_ack_message(user, linkage.ack_message, variables)

        return result, linkage, variables

    def step(self, bot, user, user_input=None, input_vars=None):
        """Main function for executing a node."""

        try:  # pylint: disable=R0101
            now = datetime.datetime.now()

            # Flag to detemine if we have jump to a node due to postback being
            # pressed. In such case global command is to checked to prevent
            # infinite loop.
            jumped = False

            g.user = user
            if user_input:
                if config.STORE_CONVERSATION:
                    Conversation(bot_id=user.bot_id, user_id=user.id,
                                 sender_enum=SenderEnum.Human,
                                 msg=user_input).add()

                user_input = user_input.RunInputTransformation()

            if user.session is None:
                user.goto(bot.start_node_id)

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
                user.goto(bot.root_node_id)

            if user_input and user_input.jump():
                jumped = True
                node = Node.get_by(id=user_input.jump_node_id, bot_id=bot.id,
                                   single=True)
                # Check if the node belongs to current bot
                if node is None:
                    logger.critical('Invalid jump node_id %d' %
                                    user_input.jump_node_id)
                # If payload button is pressed, we need to jump to the
                # corresponding node if payload's node_id != current_node_id
                elif user_input.jump_node_id != user.session.node_id:
                    user.goto(user_input.jump_node_id)
                    user.session.message_sent = True

            node = Node.get_by(id=user.session.node_id,
                               eager=['content_module', 'parser_module'],
                               single=True)
            g.node = node

            if node is None:
                logger.critical('Invalid node_id %d' % user.session.node_id)
                user.goto(bot.root_node_id)
                user.session.message_sent = True
                return self.step(bot, user, user_input)

            track(TrackingInfo.Pageview(user.platform_user_ident,
                                        '/%s' % node.name))

            # Shared global variables
            global_variables = {
                'statistic': {
                    'user_count': User.count_by(bot_id=bot.id)
                },
                'user': user.to_json()
            }

            if not user.session.message_sent:
                env = {
                    'platform_type': SupportedPlatform(
                        user.platform.type_enum.value)
                }
                # Prepare input variables
                input_vars = input_vars or {}
                input_vars.update(global_variables)

                # TODO(aitjcize): figure out how to deal with cm exceptions
                cm = node.content_module.get_module()

                # Send message
                messages = cm.run(node.content_config, env, input_vars)
                messaging.send_message(user, messages)
                user.session.message_sent = True

                # Store InputTransformation in session
                user.session.input_transformation = InputTransformation.get()

                if not node.expect_input:
                    # There are no parser module or no outgoing links. This
                    # means we are at end of subgraph.
                    n_linkages = Linkage.count_by(start_node_id=node.id)
                    if n_linkages == 0 or node.parser_module is None:
                        user.goto(bot.root_node_id)
                        user.session.message_sent = True
                        return
                    # Has parser module, parser module should be a passthrough
                    # module
                    return self.step(bot, user)
            else:
                # Don't check for global command if we are jumping to a node
                # due to postback being pressed.
                if user_input and not jumped:
                    result, link, variables = self.run_parser_module(
                        bot.root_node, user, user_input, global_variables,
                        True)

                    if result.matched:  # There is a global command match
                        if link:
                            user.goto(link.end_node_id)
                        else:
                            # There is no link, replay current node.
                            user.session.message_sent = False
                        return self.step(bot, user, user_input, variables)
                else:
                    # We are already at root node and there is no user input.
                    # Display root node again.
                    if not user_input and node.id == bot.root_node_id:
                        user.session.message_sent = False
                        return self.step(bot, user, user_input)

                # No parser module associate with this node, go back to root
                # node.
                if node.parser_module is None:
                    user.goto(bot.root_node_id)
                    user.session.message_sent = True
                    # Run at root instead, so disable jump
                    user_input.disable_jump()
                    return self.step(bot, user, user_input)

                result, link, variables = self.run_parser_module(
                    node, user, user_input, global_variables, False)

                # link may be None, either there is a bug or parser module
                # decide not to move at all.
                if link:
                    user.goto(link.end_node_id)

                    # if we are going back the same node, assume there is an
                    # error and we want to retry. don't send message in this
                    # case.
                    if (link.end_node_id == node.id and
                            node.id != bot.root_node_id and
                            result.skip_content_module):
                        user.session.message_sent = True
                        return
                else:
                    # There is no link, replay current node.
                    user.session.message_sent = False

                # Run next content module
                return self.step(bot, user, None, variables)
        except Exception as e:
            logger.exception(e)
            # Rollback when error happens, so user won't get stuck in some
            # weird state.
            DatabaseManager.rollback()
        finally:
            user.last_seen = datetime.datetime.now()
            DatabaseManager.commit()

    def process_admin_reply(self, bot, user, unused_user_input=None,
                            unused_input_vars=None):
        try:
            if bot.admin_interaction_timeout > 0:
                user.last_admin_seen = datetime.datetime.now()
        finally:
            DatabaseManager.commit()
