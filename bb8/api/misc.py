# -*- coding: utf-8 -*-
"""
    Misc API
    ~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import urllib2

from StringIO import StringIO

from flask import request, make_response
from PIL import Image

from bb8 import app
from bb8.constant import HTTPStatus, CustomError
from bb8.error import AppError


@app.route('/util/image_convert', methods=['GET'])
def image_convert_url():
    """Image convert service."""
    # TODO(aitjcize): cache converted image to S3
    try:
        url = base64.b64decode(request.args['url'])
        size = [int(x) for x in request.args['size'].split('x')]
    except Exception:
        raise AppError(HTTPStatus.STATUS_BAD_REQUEST,
                       CustomError.ERR_WRONG_PARAM,
                       'invalid request argument')

    try:
        h = urllib2.urlopen(url, timeout=5)
    except Exception:
        raise AppError(HTTPStatus.STATUS_BAD_REQUEST,
                       CustomError.ERR_INVALID_URL,
                       'invalid image url')

    buf = StringIO()
    buf.write(h.read())

    img = Image.open(buf)
    buf = StringIO()

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize not required
    if img.width < size[0] and img.height < size[1]:
        img.save(buf, 'JPEG', quality=95)
    else:
        if img.width >= img.height:
            ratio = float(size[0]) / img.width
        else:
            ratio = float(size[1]) / img.height

        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.LANCZOS)
        img.save(buf, 'JPEG', quality=95)

    response = make_response(buf.getvalue())
    response.headers['content-type'] = 'image/jpeg'

    return response
