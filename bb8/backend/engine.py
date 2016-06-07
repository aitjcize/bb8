# -*- coding: utf-8 -*-
"""
    Engine for executing logic graph
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time

from bb8 import logger

from bb8.backend import messaging
from bb8.backend.database import Linkage, Node


class Engine(object):
    BB8_GLOBAL_NOMATCH_IDENT = '$bb8.global.nomatch'

    def __init__(self):
        pass

    def run_parser_module(self, node, user_input):
        """Execute a parser module of a node, then return linkage.

        If action_ident is BB8_GLOBAL_NOMATCH_IDENT (should only happen in case
        of running root parser modele (global command). Return without
        attempting to find a linkage.
        """
        pm = node.parser_module.get_module()
        action_ident, variables = pm.run(node.parser_config, user_input)
        if action_ident == self.BB8_GLOBAL_NOMATCH_IDENT:
            return None, {}

        linkage = Linkage.get_by(start_node_id=node.id,
                                 action_ident=action_ident, single=True)
        if linkage is None:
            logger.critical('No machting linkage found for %s with '
                            'action = "%s"' % (node, action_ident))
        return linkage, variables

    def step(self, bot, user, user_input=None, input_variables=None):
        """Main function for executing a node."""

        try:
            now = time.time()

            if user.session is None:
                user.goto(bot.start_node_id)

            # Check has been idle for too long, reset it's state if yes.
            if (now - user.last_seen > bot.session_timeout or
                    not user.session):
                user.last_seen = time.time()
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
                    user.goto(user_input.jump_node_id)
                    user.session.message_sent = True

            node = Node.get_by(id=user.session.node_id,
                               eager=['content_module', 'parser_module'],
                               single=True)

            if node is None:
                logger.critical('Invalid node_id %d' % user.session.node_id)
                user.goto(bot.start_node_id)
                return self.step(bot, user, user_input)

            if not user.session.message_sent:
                env = {'node_id': node.id}
                cm = node.content_module.get_module()
                messages = cm.run(node.content_config, env, input_variables)
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
                if user_input:
                    link, variables = self.run_parser_module(bot.root_node,
                                                             user_input)
                    if link:  # There is a global command match
                        if link.ack_message:
                            messaging.send_message(
                                user, messaging.Message(link.ack_message))
                        user.goto(link.end_node_id)
                        return self.step(bot, user, user_input, variables)

                # We are already at root node and there is no match on global
                # command. Display root node again.
                if node.id == bot.root_node_id:
                    user.session.message_sent = False
                    return self.step(bot, user, user_input)

                # No parser module associate with this node, go back to root
                # node.
                if node.parser_module is None:
                    user.goto(bot.root_node_id)
                    user.session.message_sent = True
                    return self.step(bot, user, variables)

                link, variables = self.run_parser_module(node, user_input)
                if link is None:  # No matching linkage, we have a bug here.
                    return

                user.goto(link.end_node_id)

                if link.ack_message:
                    messaging.send_message(
                        user, messaging.Message(link.ack_message))

                # If we are going back the same node, assume there is an error
                # and we want to retry. Don't send message in this case.
                if link.end_node_id == node.id and node.id != bot.root_node_id:
                    user.session.message_sent = True
                    return

                # Run next content module
                self.step(bot, user, None, variables)
        finally:
            user.last_seen = time.time()
            user.commit()
