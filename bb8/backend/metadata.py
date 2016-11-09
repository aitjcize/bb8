# -*- coding: utf-8 -*-
"""
    Metadata classes
    ~~~~~~~~~~~~~~~~

    Metadata classes such as class for storing session object.

    Copyright 2016 bb8 Authors
"""

from sqlalchemy.ext.mutable import Mutable


class SessionRecord(Mutable):
    def __init__(self, node_id):
        self._node_id = node_id
        self._message_sent = False
        self._input_transformation = []

    def __repr__(self):
        return '<SessionRecord(%s, %s)>' % (self._node_id, self._message_sent)

    @property
    def node_id(self):
        return self._node_id

    @property
    def message_sent(self):
        return self._message_sent

    @message_sent.setter
    def message_sent(self, value):
        self._message_sent = value
        self.changed()

    @property
    def input_transformation(self):
        return self._input_transformation

    @input_transformation.setter
    def input_transformation(self, value):
        self._input_transformation = value
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, int):
                return SessionRecord(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return self._node_id, self._message_sent, self._input_transformation

    def __setstate__(self, state):
        try:
            (self._node_id,
             self._message_sent,
             self._input_transformation) = state
        except ValueError:
            # Temporarily workaround: We added input_transformation on
            # 2016/07/02. Need to handle the case where the previous user
            # session does not have input_transformation
            self._node_id, self._message_sent = state
            self._input_transformation = []


class ParseResult(object):
    """A result object parser modules needs to return.
    """
    def __init__(self, end_node_id=None, ack_message=None, variables=None,
                 collected_datum=None, errored=False,
                 skip_content_module=True):
        """Constructor.

        Args:
            end_node_id: end_node stable_id.
            ack_message: ack message that we want to reply immediately.
            variables: parsed action variable.
            collected_datum: data that the parser wants to collect.
            errored: whether or that there was a parser error.
            skip_content_module: skip running content module if the current
                node is executed immediately.
        """
        self.end_node_id = end_node_id
        self.ack_message = ack_message
        self.variables = variables or {}
        self.collected_datum = collected_datum or {}
        self.errored = errored
        self.skip_content_module = skip_content_module

    def collect(self, key, value):
        self.collected_datum[key] = value

    @property
    def matched(self):
        return self.end_node_id is not None or self.ack_message is not None
