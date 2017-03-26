#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    BB8 Slack Daemon
    ~~~~~~~~~~~~~~~~

    Slack bot for controlling BB8 server.

    Copyright 2016 bb8 Authors
"""

import json
import logging
import subprocess
import threading
import traceback

import websocket

from slacker import Slacker


_SLACK_TOKEN = 'xoxb-102806872243-CID1gwuenpeYcARR6M6bcrox'


def setup_logger():
    logger = logging.getLogger('websocket')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(message)s', '%Y/%m/%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def threaded(func):
    def _wrapped(self):
        if self.thread is None:
            def thread_func():
                func(self)
                self.thread = None

            self.thread = threading.Thread(target=thread_func)
            self.thread.start()
        else:
            self.post_message('An active task is running, command ignored.')
    return _wrapped


class SlackClient(object):
    def __init__(self, channel):
        self._slack = Slacker(_SLACK_TOKEN)
        self._channel = channel
        self._id = None
        self._mention = None
        self._channel_id = None
        self._ws = None
        self.thread = None

    def start(self):
        response = self._slack.rtm.start()
        self._id = response.body['self']['id']
        self._mention = '<@%s>' % self._id

        for ch in response.body['channels']:
            if ch['name'] == self._channel:
                self._channel_id = ch['id']

        if self._channel_id is None:
            raise RuntimeError('can not find channel `%s\'' % self._channel)

        self._ws = websocket.WebSocketApp(response.body['url'],
                                          on_error=self.on_error,
                                          on_close=self.on_close,
                                          on_message=self.on_message)
        self._ws.run_forever()

    def run(self, command, input_data=None, allow_error=False):
        """Simple wrapper for executing shell command."""
        try:
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            (stdout, stderr) = p.communicate(input_data)
            self.post_message('```%s```' % stdout)
            if stderr:
                self.post_message('```%s```' % stderr)
        except Exception:
            if not allow_error:
                raise Exception(stderr)

    def on_error(self, unused_ws, error):
        logging.error(error)

    def on_close(self, unused_ws):
        logging.info('connect closed')

    def on_message(self, unused_ws, msg):
        try:
            data = json.loads(msg)
            if data.get('type') == 'message':
                if data['text'].startswith(self._mention):
                    text = data['text'][len(self._mention):].lstrip()
                    self.process_command(text)
        except Exception as e:
            logging.exception(e)

    def post_message(self, message):
        self._ws.send(
            json.dumps({
                'type': 'message',
                'channel': self._channel_id,
                'text': message
            })
        )

    def pong(self):
        self.post_message('pong')

    def status(self):
        try:
            self.run('bb8ctl status')
        except Exception:
            self.post_message(traceback.format_exc())

    @threaded
    def full_deploy(self):
        try:
            self.post_message('Checking out latest code ...')
            self.run('git pull')
            self.post_message('Running `make deploy` ...')
            self.run('make deploy')
            self.post_message('Updating bots ...')
            self.run('manage update_bots', 'yes\n\n')
        except Exception:
            self.post_message(traceback.format_exc())
        else:
            self.post_message('It\'s a success ;)')

    @threaded
    def update_bots(self):
        try:
            self.post_message('Checking out latest code ...')
            self.run('git pull')
            self.post_message('Updating bots ...')
            self.run('manage update_bots', 'yes\n\n')
        except Exception:
            self.post_message(traceback.format_exc())
        else:
            self.post_message('It\'s a success ;)')

    def process_command(self, command):
        if command == 'ping':
            self.pong()
        elif command == 'status':
            self.status()
        elif command == 'full deploy':
            self.full_deploy()
        elif command == 'update bots':
            self.update_bots()


if __name__ == '__main__':
    setup_logger()
    client = SlackClient('operation')
    try:
        while True:
            client.start()
    except KeyboardInterrupt:
        pass
