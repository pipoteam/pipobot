# !/usr/bin/python
"""This file contains the class 'BotMatrix' which is a bot for Matrix Chan"""

import logging
import threading
import time

from matrix_client.client import MatrixClient

from pipobot.bot import PipoBot

logger = logging.getLogger('pipobot.bot_matrix')


class BotMatrix(PipoBot):
    """The implementation of a bot for Matrix Chan"""

    def __init__(self, login, passwd, chan, modules, session, name='pipobot', address="https://matrix.org"):
        logger.info("Connecting to %s", address)
        self.client = MatrixClient(address)
        logger.debug("login in")
        token = self.client.login_with_password(username=login, password=passwd)
        if token:
            logger.debug("logged in")
        else:
            logger.error("login failed")
        self.room = self.client.join_room(chan)
        self.room.add_listener(self.on_message)
        logger.debug("connected to %s", self.room)
        if name:
            logger.debug("set name to %s", name)
            self.client.get_user(self.client.user_id).set_display_name(name)
            self.name = name

        super(BotMatrix, self).__init__(name, login, chan, modules, session)

        logger.debug("start listener thread")
        self.client.start_listener_thread()
        self.say(_("Hi there"))
        logger.info("init done")

    def on_message(self, room, event):
        logger.debug("new event")
        if event['type'] == 'm.room.message':
            logger.debug("event is a message")
            self.message_handler(event)
        elif event['type'] == 'm.room.member':
            logger.debug("event is a presence")
            self.presence_handler(event)

    def message_handler(self, event):
        """Method called when the bot receives a message"""
        # We ignore messages in some cases :
        #   - the bot is muted
        #   - the message is empty
        if self.mute or event["content"]["body"] == "":
            return

        thread = threading.Thread(target=self.answer, args=(event,))
        thread.start()

    def answer(self, mess):
        logger.debug('handling message')
        result = self.module_answer(mess)
        if type(result) is list:
            for to_send in result:
                self.say(to_send)
        else:
            self.say(result)
        logger.debug('handled message')

    def kill(self):
        """Method used to kill the bot"""

        # The bot says goodbye
        self.say(_("I’ve been asked to leave you"))
        # The bot leaves the room
        self.client.logout()
        self.stop_modules()
        logger.info('killed')

    def say(self, msg, priv=None, in_reply_to=None):
        """The method to call to make the bot sending messages"""
        # If the bot has not been disabled
        logger.debug('say %s', msg)
        if not self.mute:
            if type(msg) is str:
                self.room.send_text(msg)
            elif type(msg) is list:

                for line in msg:
                    time.sleep(0.3)
                    self.room.send_text(line)
            elif type(msg) is dict:
                if "users" in msg:
                    pass
                else:
                    if "xhtml" in mess:
                        mess_xhtml = "<p>%s</p>" % mess["xhtml"]
                        self.room.send_html(mess_xhtml, msg["text"])
                    else:
                        self.room.send_text(msg["text"])

    def presence_handler(self, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and roles"""
        pass
