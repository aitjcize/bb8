# -*- coding: utf-8 -*-
"""
    Request Context Task
    ~~~~~~~~~~~~~~~~~~~~

    Base class for Celery tasks running inside Flask request context.

    This code snippet is take from:
    http://xion.io/post/code/celery-include-flask-request-context.html
    https://gist.github.com/Xion/46d739b980af14a0d3ea

    Copyright 2016 bb8 Authors
"""

from celery import Task
from flask import has_request_context, make_response, request

from bb8 import app
from bb8.backend.database import DatabaseSession


__all__ = ['RequestContextTask']


class RequestContext(object):
    def __init__(self, req):
        self.path = req.path
        self.base_url = req.base_url
        self.method = req.method
        self.headers = dict(req.headers)
        self.data = req.data
        self.query_string = None
        if '?' in req.url:
            self.query_string = req.url[(req.url.find('?') + 1):]

    def __repr__(self):
        return '<RequestContext>'

    def as_dict(self):
        return {
            'path': self.path,
            'base_url': self.base_url,
            'method': self.method,
            'headers': self.headers,
            'data': self.data,
            'query_string': self.query_string
        }


# pylint: disable=W0223
class RequestContextTask(Task):
    """Base class for tasks that originate from Flask request handlers
    and carry over most of the request context data.

    This has an advantage of being able to access all the usual information
    that the HTTP request has and use them within the task. Pontential
    use cases include e.g. formatting URLs for external use in emails sent
    by tasks.
    """
    abstract = True

    #: Name of the additional parameter passed to tasks
    #: that contains information about the original Flask request context.
    CONTEXT_ARG_NAME = '_flask_request_context'

    def __call__(self, *args, **kwargs):
        """Execute task code with given arguments."""
        def call():
            return super(RequestContextTask, self).__call__(*args, **kwargs)

        context = kwargs.pop(self.CONTEXT_ARG_NAME, None)
        if context is None or has_request_context():
            return call()

        with app.test_request_context(**context.as_dict()):
            with DatabaseSession():
                result = call()
                # process a fake "Response" so that
                # ``@after_request`` hooks are executed
                app.process_response(make_response(result or ''))

        return result

    def apply_async(self, args=None, kwargs=None, **rest):
        args = args or []
        kwargs = kwargs or {}
        if rest.pop('with_request_context', True):
            self._include_request_context(kwargs)
        return super(RequestContextTask, self).apply_async(args, kwargs,
                                                           **rest)

    def apply(self, args=None, kwargs=None, **rest):
        args = args or []
        kwargs = kwargs or {}
        if rest.pop('with_request_context', True):
            self._include_request_context(kwargs)
        return super(RequestContextTask, self).apply(args, kwargs, **rest)

    def retry(self, args=None, kwargs=None, **rest):
        args = args or []
        kwargs = kwargs or {}
        if rest.pop('with_request_context', True):
            self._include_request_context(kwargs)
        return super(RequestContextTask, self).retry(args, kwargs, **rest)

    def _include_request_context(self, kwargs):
        """Includes all the information about current Flask request context
        as an additional argument to the task.
        """
        if not has_request_context():
            return
        kwargs[self.CONTEXT_ARG_NAME] = RequestContext(request)
