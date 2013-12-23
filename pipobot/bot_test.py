#!/usr/bin/python
#-*- coding: utf-8 -*-
"""This module contains a class to test the bot in a CLI mode"""

import logging
from pipobot.bot import PipoBot

logger = logging.getLogger('pipobot.bot_jabber')


class ForgedFrom:
    def __init__(self, frm):
        self.resource = frm


class ForgedMsg(dict):
    def __init__(self, sender, body):
        self["from"] = ForgedFrom(sender)
        self["type"] = "groupchat"
        self["body"] = body


class TestBot(PipoBot):
    def __init__(self, name, login, chatname, modules, session):
        PipoBot.__init__(self, name, login, chatname, modules, session)
        self.occupants.add_user(name, login, "moderator")

        logger.info("Starting console bot in fake room %s" % self.chatname)

        self.session = session

        # Since we are in test mode, we remove time constraints
        for module in self._modules.sync.values():
            if hasattr(module, "lock_name"):
                del module.lock_name

    def create_msg(self, frm, content):
        """ Creates a fake message and returns the bot response """
        msg = ForgedMsg(frm, content)
        return self.message(msg)

    def decode_module_message(self, msg):
        """ Extracts the 'text' value of a message return by BotJabber.answer """
        if msg is not None:
            if type(msg) is dict:
                res = ""
                if "users" in msg:
                    for usr, message in msg["users"].iteritems():
                        if "nopriv" in message and message["nopriv"]:
                            res += "\n%s" % (self.decode_module_message(message))
                        else:
                            res += "\n<priv %s> : %s" % (usr, self.decode_module_message(message))
                else:
                    res = msg["text"]
            elif type(msg) is list:
                res = "\n".join(self.decode_module_message(m) for m in msg)
            elif type(msg) is tuple:
                res = msg[0]
            elif type(msg) is str:
                res = msg
            elif type(msg) is unicode:
                res = msg.decode("utf-8")
            return res.strip()

    def message(self, mess):
        """Method called when the bot receives a message"""
        #We ignore messages in some cases :
        #   - it has a subject (change of room topic for instance)
        #   - it is a 'delay' message (backlog at room join)
        #   - the message is empty
        ret = self.module_answer(mess)
        if type(ret) is list:
            result = "\n".join(map(self.decode_module_message, ret))
        else:
            result = self.decode_module_message(ret)
        return result

    def say(self, *args, **kwargs):
        """The method to call to make the bot sending messages"""
        #In test mode, say does nothing !
        return args[0]

    def say_xhtml(self, *args, **kwargs):
        """Method to talk in xhtml"""
        #If the bot has not been disabled
        return self.say(args, kwargs)

    def kill(self):
        self.stop_modules()
