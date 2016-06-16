# -*- coding: utf-8 -*-
"""
    Third party web services
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import urllib

from flask import request, make_response

from bb8 import app

from bb8.backend.content_modules.youbike import GOOGLE_STATIC_MAP_API_KEY


@app.route('/third_party/youbike/render_map')
def redirect_url():
    """Workaround facebooks 'bug', wher it remove multiple value with same key.
    We use facebook to pass the arguments, then request render from Google on
    behalf of it."""

    url = request.args.get('url', None)
    if not url:
        return 'No URL specified'

    url = urllib.unquote(url + '&key=' + GOOGLE_STATIC_MAP_API_KEY)
    h = urllib.urlopen(url)
    response = make_response(h.read())
    response.headers['content-type'] = h.headers['content-type']

    return response
