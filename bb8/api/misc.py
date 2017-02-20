# -*- coding: utf-8 -*-
"""
    Misc API
    ~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import hashlib
import os
import shutil
import tempfile
import urllib2
import urlparse
from cStringIO import StringIO

import requests

from flask import g, redirect, request, make_response
from gcloud import storage
from PIL import Image

from bb8 import app, config
from bb8.api.error import AppError
from bb8.backend.database import Bot
from bb8.constant import HTTPStatus, CustomError
from bb8.tracking import track, TrackingInfo


ALLOWED_HOSTS = ['dramaq.biz', 'www.dramaq.biz', 'showq.biz', 'www.showq.biz',
                 'cdn.parenting.com.tw']


@app.route('/api/util/cache_image', methods=['GET'])
def cache_image():
    """Cache the image and return the cached URL."""
    gs_client = storage.Client(project=config.GCP_PROJECT)
    bucket = gs_client.get_bucket('cached-pictures')
    url = request.args['url']
    host = urlparse.urlparse(url).netloc

    if not url:
        raise AppError(HTTPStatus.STATUS_BAD_REQUEST,
                       CustomError.ERR_WRONG_PARAM,
                       'invalid request argument')

    if host not in ALLOWED_HOSTS:
        return redirect(url)

    ext = url.split('.')[-1]
    if ext not in ['jpg', 'jpeg', 'png', 'gif']:
        raise AppError(HTTPStatus.STATUS_BAD_REQUEST,
                       CustomError.ERR_WRONG_PARAM,
                       'invalid request argument')

    url_hash = hashlib.sha1(url).hexdigest()
    hash_name = '%s.%s' % (url_hash, ext)

    blob = bucket.get_blob(hash_name)
    if blob:
        return redirect(blob.media_link)

    response = requests.get(url, stream=True)

    # If the request failed, ignore and just redirect user to it.
    if response.status_code != 200:
        return redirect(url)

    with tempfile.NamedTemporaryFile(delete=False) as fio:
        shutil.copyfileobj(response.raw, fio)

    blob = storage.blob.Blob(hash_name, bucket)
    blob.upload_from_filename(fio.name, response.headers.get('Content-Type'))
    os.unlink(fio.name)

    return redirect(blob.public_url)


@app.route('/api/util/image_convert', methods=['GET'])
def image_convert_url():
    """Image convert service."""
    try:
        url = base64.b64decode(request.args['url'])
        size = [int(x) for x in request.args['size'].split('x')]
    except Exception:
        raise AppError(HTTPStatus.STATUS_BAD_REQUEST,
                       CustomError.ERR_WRONG_PARAM,
                       'invalid request argument')

    mode = request.args.get('mode')

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
    if float(img.width) / img.height > float(size[0]) / float(size[1]):
        ratio = float(size[0]) / img.width
    else:
        ratio = float(size[1]) / img.height

    img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                     Image.LANCZOS)

    if mode == 'pad':
        pad_color = request.args.get('pad_color', 'white')
        new_img = Image.new('RGB', tuple(size), pad_color)
        new_img.paste(img, ((size[0] - img.width) / 2,
                            (size[1] - img.height) / 2))
        img = new_img

    img.save(buf, 'JPEG', quality=95)

    response = make_response(buf.getvalue())
    response.headers['content-type'] = 'image/jpeg'

    return response


@app.route('/api/r/<int:bot_id>/<platform_user_ident>')
def redirect_track_url(bot_id, platform_user_ident):
    """Handler for tracking URL

    This handler allow us to track 'web_url' button clicks by embedding the
    tracking info in the url parameters and sending to GA.
    """
    url = request.args.get('url', None)
    if not url:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'No URL specified')

    path = request.args.get('path', None)
    if not path:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'No path specified')

    try:
        ret = Bot.query(Bot.ga_id).filter_by(id=bot_id).one()
    except Exception:
        raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                       CustomError.ERR_WRONG_PARAM,
                       'Internal Error')

    g.ga_id = ret[0]
    track(TrackingInfo.Pageview(platform_user_ident, '/Redirect/%s' % path))

    return redirect(url)
