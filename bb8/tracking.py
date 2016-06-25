# -*- coding: utf-8 -*-
"""
    Tracking Utilities
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import enum
import requests

from flask import g

from bb8 import config, logger


class TrackingInfo(object):
    class Type(enum.Enum):
        Pageview = 'pageview'
        Event = 'event'

    def __init__(self):
        self.ttype = None
        self.page = None
        self.catagory = None
        self.action = None
        self.label = None
        self.value = None

    @classmethod
    def to_utf8(cls, val):
        return val.encode('utf8') if isinstance(val, unicode) else val

    @classmethod
    def Pageview(cls, page):
        t = cls()
        t.ttype = cls.Type.Pageview
        t.page = cls.to_utf8(page).replace(' ', '-')
        return t

    @classmethod
    def Event(cls, catagory, action, label, value=1):
        t = cls()
        t.ttype = cls.Type.Event

        t.catagory = cls.to_utf8(catagory)
        t.action = cls.to_utf8(action)
        t.label = cls.to_utf8(label)
        t.value = value
        return t


def track(trackinginfo):
    """Track a single event and put it in the global context."""
    if not isinstance(trackinginfo, TrackingInfo):
        raise RuntimeError('invalid tracking info')
    try:
        _ = g.tracking
    except AttributeError:
        g.tracking = []

    g.tracking.append(trackinginfo)


def send_ga_track_info(tracking):
    """Send tracking info to GA."""
    # Only track when we are in production mode.
    if not config.DEPLOY:
        return

    base = 'v=1&tid=%s&cid=12345' % config.YOUBIKE_BOT_GA_ID
    params = ''
    for ti in tracking:
        if ti.ttype == TrackingInfo.Type.Event:
            params += base + '&'.join([
                '',
                't=%s' % ti.ttype.value,
                'ec=%s' % ti.catagory,
                'ea=%s' % ti.action,
                'el=%s' % ti.label,
                'ev=%s' % ti.value]) + '\n'
        elif ti.ttype == TrackingInfo.Type.Pageview:
            params += base + '&'.join([
                '',
                't=%s' % ti.ttype.value,
                'dp=%s' % ti.page]) + '\n'

    response = requests.request(
        'POST',
        'http://www.google-analytics.com/batch',
        data=params)

    if response.status_code != 200:
        logger.error('send_ga_track_info: HTTP %d: %s' %
                     (response.status_code, response.text))
