# -*- coding: utf-8 -*-
"""
    Speech Recogintion Service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import contextlib
import subprocess
import urllib2

import requests

from bb8 import config

GOOGLE_SPEECH_API_URL = ('https://speech.googleapis.com/v1beta1/'
                         'speech:syncrecognize')
TIMEOUT = 5


def convert_to_wav(url):
    """Convert given audio file to wav format.

    Args:
        url: url to the audio file

    Returns:
        Return converted audio content as python string.
    """

    with contextlib.closing(urllib2.urlopen(url, timeout=TIMEOUT)) as f:
        data = f.read()

    p = subprocess.Popen('ffmpeg -i - -f wav - 2>/dev/null', shell=True,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, unused_stderr = p.communicate(data)
    return stdout


def speech_to_text(url, language='en_US'):
    """Convert speech to text."""
    audio_data = convert_to_wav(url)

    req = {
        'config': {
            'encoding': 'LINEAR16',
            'sampleRate': 8000,
            'languageCode': language,
            'maxAlternatives': 1
        },
        'audio': {
            'content': base64.b64encode(audio_data)
        }
    }

    response = requests.request(
        'POST',
        GOOGLE_SPEECH_API_URL,
        headers={'Authorization': 'Bearer %s' % config.GCLOUD_ACCESS_TOKEN},
        json=req)

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))
    try:
        return response.json()['results'][0]['alternatives'][0]['transcript']
    except Exception:
        return None
