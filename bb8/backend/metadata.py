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
        self._input_transformation = []

    def __repr__(self):
        return '<SessionRecord(%s)>' % (self._node_id)

    @property
    def node_id(self):
        return self._node_id

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
        return self._node_id, self._input_transformation

    def __setstate__(self, state):
        (self._node_id,
         self._input_transformation) = state


class ModuleResult(object):
    def __init__(self, messages=None, variables=None, memory=None):
        self.messages = messages or []
        self.variables = variables or {}
        self.memory = memory or {}


class RouteResult(object):
    """A result object router modules needs to return.
    """
    def __init__(self, end_node_id=None, ack_message=None, variables=None,
                 errored=False):
        """Constructor.

        Args:
            end_node_id: end_node stable_id.
            ack_message: ack message that we want to reply immediately.
            variables: parsed action variable.
            errored: whether or that there was an error.
        """
        self.end_node_id = end_node_id
        self.ack_message = ack_message
        self.variables = variables or {}
        self.errored = errored

    @property
    def matched(self):
        return self.end_node_id is not None or self.ack_message is not None
