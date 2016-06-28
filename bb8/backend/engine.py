# -*- coding: utf-8 -*-
"""
    Engine for executing logic graph
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import random

from bb8 import logger

from bb8.backend import messaging
from bb8.tracking import track, TrackingInfo
from bb8.backend.database import (g, ColletedDatum, Linkage, Node,
                                  SupportedPlatform, User)


class Engine(object):
    BB8_GLOBAL_NOMATCH_IDENT = '$bb8.global.nomatch'

    def __init__(self):
        pass

    def send_ack_message(self, user, link, variables):
        """Respond user with *link.ack_message*.

        Args:
            user: the User object.
            link: Linkage object. link.ack_message could either be a string or
                a list of string. If it is a list of string, we randomly select
                one of the string to send.
            variables: variables for rendering text
        """
        ack_message = link.ack_message
        if not ack_message:  # ack message could be empty string or []
            return

        if isinstance(ack_message, list):
            ack_message = random.choice(ack_message)

        messaging.send_message(user, messaging.Message(ack_message,
                                                       variables=variables))

    def insert_data(self, user, data):
        """Insert collected data into database."""
        for key in data:
            ColletedDatum(user_id=user.id, key=key, value=data[key]).add()

    def run_parser_module(self, node, user, user_input, as_root=False):
        """Execute a parser module of a node, then return linkage.

        If action_ident is BB8_GLOBAL_NOMATCH_IDENT (should only happen in case
        of running root parser modele (global command). Return without
        attempting to find a linkage.
        """
        pm = node.parser_module.get_module()
        action_ident, variables, data = pm.run(node.parser_config, user_input,
                                               as_root)

        # Global parser nomatch
        if action_ident == self.BB8_GLOBAL_NOMATCH_IDENT:
            return None, {}

        # Collect data
        self.insert_data(user, data)

        # Track error
        if action_ident == '$error':
            track(TrackingInfo.Event(user.platform_user_ident,
                                     'Parser', 'Error', user_input.text))

        linkage = Linkage.get_by(start_node_id=node.id,
                                 action_ident=action_ident, single=True)
        if linkage is None:
            logger.critical('No machting linkage found for %s with '
                            'action = "%s"' % (node, action_ident))
        return linkage, variables

    def step(self, bot, user, user_input=None, input_vars=None):
        """Main function for executing a node."""

        try:
            now = datetime.datetime.now()

            # Flag to detemine if we have jump to a node due to postback being
            # pressed. In such case global command is to checked to prevent
            # infinite loop.
            jumped = False

            if user.session is None:
                user.goto(bot.start_node_id)

            # Check has been idle for too long, reset it's state if yes.
            if ((now - user.last_seen).total_seconds() > bot.session_timeout or
                    not user.session):
                user.last_seen = datetime.datetime.now()
                user.goto(bot.start_node_id)

            if user_input and user_input.jump():
                node = Node.get_by(id=user_input.jump_node_id, bot_id=bot.id,
                                   single=True)
                # Check if the node belongs to current bot
                if node is None:
                    logger.critical('Invalid jump node_id %d' %
                                    user_input.jump_node_id)
                # If payload button is pressed, we need to jump to the
                # corresponding node if payload's node_id != current_node_id
                elif user_input.jump_node_id != user.session.node_id:
                    jumped = True
                    user.goto(user_input.jump_node_id)
                    user.session.message_sent = True

            node = Node.get_by(id=user.session.node_id,
                               eager=['content_module', 'parser_module'],
                               single=True)
            if node is None:
                logger.critical('Invalid node_id %d' % user.session.node_id)
                user.goto(bot.root_node_id)
                user.session.message_sent = True
                return self.step(bot, user, user_input)

            track(TrackingInfo.Pageview(user.platform_user_ident,
                                        '/%s' % node.name))

            # Inject global reference
            g.node = node
            g.user = user

            def populate_env_variables(variables):
                """Populate environment variables."""
                variables = variables or {}
                variables['statistic'] = {
                    'user_count': User.count_by(bot_id=bot.id)
                }
                variables['user'] = user.to_json()
                return variables

            if not user.session.message_sent:
                env = {
                    'platform_type': SupportedPlatform(
                        user.platform.type_enum.value)
                }
                # Prepare input variables
                input_vars = populate_env_variables(input_vars)
                g.variables = input_vars

                # TODO(aitjcize): figure out how to deal with cm exceptions
                cm = node.content_module.get_module()
                messages = cm.run(node.content_config, env, input_vars)
                messaging.send_message(user, messages)
                user.session.message_sent = True

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
                # Don't check for global command if we are jumping to a ndoe
                # due to postback being pressed.
                if user_input and not jumped:
                    link, variables = self.run_parser_module(
                        bot.root_node, user, user_input, True)

                    if link:  # There is a global command match
                        self.send_ack_message(user, link, variables)
                        user.goto(link.end_node_id)
                        return self.step(bot, user, user_input, variables)
                else:
                    # We are already at root node and there is no user input.
                    # Display root node again.
                    if node.id == bot.root_node_id:
                        user.session.message_sent = False
                        return self.step(bot, user, user_input)

                # No parser module associate with this node, go back to root
                # node.
                if node.parser_module is None:
                    user.goto(bot.root_node_id)
                    user.session.message_sent = True
                    return self.step(bot, user, None, variables)

                link, variables = self.run_parser_module(
                    node, user, user_input, False)

                if link is None:  # No matching linkage, we have a bug here.
                    return

                self.send_ack_message(user, link, variables)
                user.goto(link.end_node_id)

                # If we are going back the same node, assume there is an error
                # and we want to retry. Don't send message in this case.
                if link.end_node_id == node.id and node.id != bot.root_node_id:
                    user.session.message_sent = True
                    return

                # Run next content module
                self.step(bot, user, None, variables)
        finally:
            user.last_seen = datetime.datetime.now()
            user.commit()
