#!/usr/bin/python
#-*- coding: utf-8 -*-
"""This module contains a class to test the bot in a CLI mode"""

import logging
from pipobot.lib.modules import (AsyncModule, ListenModule,
                                 MultiSyncModule, PresenceModule,
                                 SyncModule, IQModule)
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.bot_jabber')


class ForgedFrom:
    def __init__(self, frm):
        self.resource = frm


class ForgedMsg(dict):
    def __init__(self, sender, body):
        self["from"] = ForgedFrom(sender)
        self["type"] = "groupchat"
        self["body"] = body


class TestBot:
    def __init__(self, modules, session):

        self.chatname = "test@unit_test.tld"
        self.name = "pipotest"

        logger.info("Starting console bot in fake room %s" % self.chatname)

        self.session = session

        # Creating bot module instances
        self.modules = []
        for classe in modules:
            logger.debug("Registering %s", classe)
            obj = classe(self)
            # Since we are in test mode, we remove time constraints
            if isinstance(obj, SyncModule):
                if hasattr(obj, "lock_name"):
                    del obj.lock_name
            if isinstance(obj, AsyncModule):
                obj.start()
            self.modules.append(obj)

        #If set to True, the bot will not be able to send messages
        self.mute = False
        self.alive = True

        #We will stock in it informations about users that join/leave
        self.occupants = Occupants()

    def create_msg(self, frm, content):
        """ Creates a fake message and returns the bot response """
        msg = ForgedMsg(frm, content)
        return self.message(msg)

    def decode_module_message(self, msg):
        """ Extracts the 'text' value of a message return by BotJabber.answer """
        if msg is not None:
            if type(msg) is dict:
                res = msg["text"]
            elif type(msg) is list:
                res = "\n".join(msg)
            elif type(msg) is tuple:
                res = msg[0]
            elif type(msg) is str:
                res = msg
            elif type(msg) is unicode:
                res = msg.decode("utf-8")
            return res

    def message(self, mess):
        """Method called when the bot receives a message"""
        #We ignore messages in some cases :
        #   - it has a subject (change of room topic for instance)
        #   - it is a 'delay' message (backlog at room join)
        #   - the message is empty
        if self.mute:
            return

        #First we look if a SyncModule matches
        for module in self.modules:
            if (isinstance(module, SyncModule) or
                isinstance(module, MultiSyncModule)):
                ret = module.do_answer(mess)
                if ret is not None:
                    ret = self.decode_module_message(ret)
                    return ret

        ret = None
        #If no SyncModule was concerned by the message, we look for a ListenModule
        for module in self.modules:
            if isinstance(module, ListenModule):
                rep = module.do_answer(mess)
                ret = self.decode_module_message(rep)

        return ret


    def forge_message(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        return mess

    def forge_xhtml(self, mess, mess_xhtml, priv=None, in_reply_to=None):
        """Sending an xhtml message in the room"""

        #The message is created from mess, in case some clients does not support XHTML (xep-0071)
        return self.forge_message(mess, priv, in_reply_to)

    def say(self, *args, **kwargs):
        """The method to call to make the bot sending messages"""
        #In test mode, say does nothing !
        return args[0]

    def say_xhtml(self, *args, **kwargs):
        """Method to talk in xhtml"""
        #If the bot has not been disabled
        return self.say(args, kwargs)

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False

    def kill(self):
        for module in self.modules:
            if isinstance(module, ListenModule):
                module.stop()
        return
