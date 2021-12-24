# !/usr/bin/python
"""This file contains the class 'BotMattermost' which is a bot for Mattermost API"""

import logging
import threading
import time
from json import loads, dumps
from websocket import create_connection
import requests

from pipobot.bot import PipoBot

logger = logging.getLogger('pipobot.bot_mattermost')


class MattermostException(Exception):
    """ For errors due to Mattermost (conflict, connection/authentification failed, …) """
    pass


class BotMattermost(PipoBot):
    """The implementation of a bot for a Mattermost instance"""

    def __init__(self, login, passwd, modules, session, address, default_team, default_channel):
        address += '/api/v4'
        self.address = address
        auth = requests.post('https://%s/users/login' % address, json={'login_id': login, 'password': passwd})

        if auth.status_code != 200:
            logger.error(_("Unable to connect !"))
            raise MattermostException(_("Unable to connect !"))

        self.headers = {'Authorization': 'Bearer %s' % auth.headers['Token']}
        self.user_id = requests.get('https://%s/users/me' % address, headers=self.headers).json()['id']
        team_url = 'https://%s/teams/name/%s' % (address, default_team)
        self.default_team_id = requests.get(team_url, headers=self.headers).json()['id']
        channel_url = 'https://%s/teams/%s/channels/name/%s' % (address, self.default_team_id, default_channel)
        self.default_channel_id = requests.get(channel_url, headers=self.headers).json()['id']

        challenge = dumps({"seq": 1, "action": "authentication_challenge", "data": {'token': auth.headers['Token']}})
        logger.debug('creating WS')
        self.ws = create_connection('wss://%s/websocket' % address)
        logger.debug('Sending challenge')
        self.ws.send(challenge)

        if not self.ws.connected:
            logger.error(_("Unable to authenticate websocket !"))
            raise MattermostException(_("Unable to authenticate websocket !"))

        super(BotMattermost, self).__init__('...', login, default_channel, modules, session)

        self.thread = threading.Thread(name='mattermost_' + default_channel, target=self.process)
        self.thread.start()
        self.say(_("Hi there"))

    def process(self):
        self.run = True
        while self.run:
            msg = loads(self.ws.recv())
            self.message_handler(msg)


    def message_handler(self, msg):
        """Method called when the bot receives a message"""
        if self.mute or 'event' not in msg or msg['event'] != 'posted':
            return

        thread = threading.Thread(target=self.answer, args=(msg,))
        thread.start()

    def answer(self, mess):
        post = loads(mess['data']['post'])
        message = {'body': post['message'], 'from': DummySender(mess['data']['sender_name']), 'type': 'chat'}
        result = self.module_answer(message)
        kwargs = {'root_id': post['parent_id'], 'channel_id': post['channel_id']}
        if type(result) is list:
            for to_send in result:
                self.say(to_send, **kwargs)
        elif type(result) is dict:
            to_send = result['text'] if 'text' in result else result['xhtml']
            if 'monospace' in result and result['monospace']:
                to_send = '`%s`' % to_send
            self.say(to_send, **kwargs)
        else:
            self.say(result, **kwargs)

    def kill(self):
        """Method used to kill the bot"""

        self.say(_("I’ve been asked to leave you"))
        self.run = False
        self.ws.close()
        self.stop_modules()

    def say(self, msg, channel_id=None, root_id=""):
        """The method to call to make the bot sending messages"""
        # If the bot has not been disabled
        if not self.mute:
            if channel_id is None:
                channel_id = self.default_channel_id
            create_at = int(time.time() * 1000)
            r = requests.post('https://%s/posts' % self.address, headers=self.headers, json={
                'channel_id': channel_id,
                'message': msg,
                'root_id': root_id
            }).json()
            if 'status_code' in r:
                logger.error(_('error in sent message %s:\nresult is: %s' % (msg, r)))


class DummySender(object):
    def  __init__(self, sender):
        self.resource = sender
