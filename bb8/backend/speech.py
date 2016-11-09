# -*- coding: utf-8 -*-
"""
    Speech Recogintion Service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import subprocess

import requests

from oauth2client.client import GoogleCredentials


GOOGLE_SPEECH_API_URL = ('https://speech.googleapis.com/v1beta1/'
                         'speech:syncrecognize')


def convert_to_wav(data):
    """Convert given audio file to wav format.

    Args:
        data: raw audio file data

    Returns:
        Return converted audio content as python string.
    """
    p = subprocess.Popen('ffmpeg -i - -f wav - 2>/dev/null', shell=True,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, unused_stderr = p.communicate(data)
    return stdout


def speech_to_text(data, language='en_US'):
    """Convert speech to text."""
    audio_data = convert_to_wav(data)

    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    access_token = credentials.get_access_token().access_token

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
        headers={'Authorization': 'Bearer %s' % access_token},
        json=req)

    if response.status_code != 200:
        raise RuntimeError('HTTP %d: %s' % (response.status_code,
                                            response.text))
    try:
        return response.json()['results'][0]['alternatives'][0]['transcript']
    except Exception:
        return None
