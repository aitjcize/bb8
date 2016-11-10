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
        self.cid = None
        self.ttype = None
        self.page = None
        self.catagory = None
        self.action = None
        self.label = None
        self.value = None
        self.ref = None

    @classmethod
    def Pageview(cls, cid, page, ref=None):
        t = cls()
        t.cid = cid
        t.ttype = cls.Type.Pageview
        t.page = page.replace(' ', '-')
        t.ref = ref
        return t

    @classmethod
    def Event(cls, cid, catagory, action, label, value=1):
        t = cls()
        t.cid = cid
        t.ttype = cls.Type.Event
        t.catagory = catagory
        t.action = action
        t.label = label
        t.value = value
        return t


def get_tracking():
    """Get tracking object. Create one if not exists."""
    try:
        _ = g.tracking
    except AttributeError:
        g.tracking = []

    return g.tracking


def enable_tracking():
    return config.DEPLOY and hasattr(g, 'ga_id') and g.ga_id


def track(trackinginfo):
    """Track a single event and put it in the global context."""
    if not isinstance(trackinginfo, TrackingInfo):
        raise RuntimeError('invalid tracking info')

    if not enable_tracking():
        return

    get_tracking().append(trackinginfo)


def send_ga_track_info():
    """Send tracking info to GA."""
    tracking = get_tracking()

    if not enable_tracking() or not tracking:
        return

    base = u'v=1&tid=%s' % g.ga_id
    params = u''
    for ti in tracking:
        if ti.ttype == TrackingInfo.Type.Event:
            params += base + u'&'.join([
                u'',
                u'cid=%s' % ti.cid,
                u't=%s' % ti.ttype.value,
                u'ec=%s' % ti.catagory,
                u'ea=%s' % ti.action,
                u'el=%s' % ti.label,
                u'ev=%s' % ti.value]) + '\n'
        elif ti.ttype == TrackingInfo.Type.Pageview:
            params += base + u'&'.join([
                u'',
                u'cid=%s' % ti.cid,
                u't=%s' % ti.ttype.value,
                u'dp=%s' % ti.page
            ] + [u'dr=%s' % ti.ref] if ti.ref else []) + '\n'

    response = requests.request(
        'POST',
        'http://www.google-analytics.com/batch',
        data=params.encode('utf8'))

    if response.status_code != 200:
        logger.error('send_ga_track_info: HTTP %d: %s' %
                     (response.status_code, response.text))
