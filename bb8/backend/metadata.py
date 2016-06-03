# -*- coding: utf-8 -*-
"""
    Metadata classes
    ~~~~~~~~~~~~~~~~

    Metadata classes such as class for storing session object.

    Copyright 2016 bb8 Authors
"""

from sqlalchemy.ext.mutable import Mutable, MutableList, MutableComposite


class SessionStack(MutableList):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, list):
                s = SessionStack()
                for i, x in enumerate(value):
                    s.append(SessionRecord.coerce(i, x))
                return s
            return MutableList.coerce(key, value)
        else:
            return value

    def __repr__(self):
        return '<SessionStack(%s)>' % (super(SessionStack, self).__repr__())

    def __hash__(self):
        return hash(str(self))

    def refresh(self, index):
        """Temporarily solution for force update of list value...
        Remove this until we can figure out a better way to perform mutation
        tracking on list."""
        # TODO(aitjcize): remove this and replace with mutation tracking
        self[index] = self[index]


class SessionRecord(MutableComposite):
    def __init__(self, node_id):
        self._node_id = node_id
        self._message_sent = False

    def __repr__(self):
        return '<SessionRecord(%d, %s)>' % (self._node_id, self._message_sent)

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

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, int):
                return SessionRecord(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return self._node_id, self._message_sent

    def __setstate__(self, state):
        self._node_id, self._message_sent = state
