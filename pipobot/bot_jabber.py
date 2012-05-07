#!/usr/bin/python
#-*- coding: utf8 -*-
"""This file contains the class 'BotJabber' wich is a bot for jabber MUC"""

import logging
import threading
import sleekxmpp
import xml.parsers.expat

from pipobot.lib.modules import AsyncModule, ListenModule, MultiSyncModule, PresenceModule, SyncModule, IQModule
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.bot_jabber') 

class XMPPException(Exception):
    """ For errors due to XMPP (conflict, connection/authentification failed, …) """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class BotJabber(sleekxmpp.ClientXMPP):
    """The implementation of a bot for jabber MUC"""
    
    def __init__(self, login, passwd, res, chat, name, xmpp_log = None, manager = None):
        self.chatname = chat
        self.manager = manager
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0199')

        sleekxmpp.ClientXMPP.__init__(self, login, passwd, ssl = True)

        logger.info(_("Connecting to %s") % chat)
        #Connecting
        con = self.connect(reattempt = False)
        if not con:
            logger.error(_("Unable to connect !"))
            raise XMPPException(_("Unable to connect !"))

        self.registerPlugin("xep_0045")

        #When the session start (bot connected) the connect_muc method will be called
        self.add_event_handler("session_start", self.connect_muc)

        #sleekxmpp handlers to XMPP stanzas
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.disconnected)
        self.add_event_handler("groupchat_presence", self.presence)

#        #xmpppy handlers to XMPP stanzas
#        self.RegisterHandler('iq', self.iq)

        self.modules = []

        #If set to True, the bot will not be able to send messages
        self.mute = False
        self.alive = True 
        
        #The nickname the bot will use to join rooms
        #This nickname will be set by the reception of a presence message after joining the room
        self.name = name

        #We will stock in it informations about users that join/leave
        self.occupants = Occupants()

        for module in self.modules:
            if isinstance(module, AsyncModule):
                module.start()
        
        self.process(threaded = True)

    def connect_muc(self, event):
        self.send_presence()
        muc = self.plugin["xep_0045"]
        join = muc.joinMUC(self.chatname, self.name)
        hello_msg = _("Hello everyone !")
        self.send_message(mto = self.chatname, mbody = hello_msg, mtype = "groupchat")

    def disconnected(self, event):
        for module in self.modules:
            if type(module) == AsyncModule:
                module.stop()

    def message(self, mess):
        """Method called when the bot receives a message"""
        #We ignore messages in some cases : 
        #   - it has a subject (change of room topic for instance)
        #   - it is a 'delay' message (backlog at room join)
        #   - the message is empty
        if self.mute                         \
           or mess["subject"] != ""  \
           or mess["body"] == "" :
                return
        
        #We look for a module which is concerned by the message
        for module in self.modules:
            if isinstance(module, ListenModule) or isinstance(module, SyncModule) or isinstance(module, MultiSyncModule):
                module.do_answer(mess)

    def add_commands(self, classes):
        """Method called when we specify modules' classes, 
            at the creation of bot instance"""
        #We instanciate all modules and then add them to the self.modules list
        for classe in classes:
            logger.debug("Registering %s" % classe)
            objet = classe(self)
            self.modules.append(objet)

    def kill(self):
        """Method used to kill the bot"""

        #We kill the thread
        self.alive = False
        #The bot says goodbye
#        self.say(_("I've been asked to leave you"))
        #The bot leaves the room
        logger.info("Killing %s" % self.chatname)
        try:
            self.disconnect()
        except xml.parsers.expat.ExpatError:
            pass

    def forge_message(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        mto = self.chatname
        mtyp = "groupchat"
        if priv:
            mto = "%s/%s" % (self.chatname, priv)
            mtyp = "chat"

        if in_reply_to:
            mtyp = in_reply_to["type"]
            if mtyp == "chat":
                mto = in_reply_to["from"]

        return mto, mess, mtyp

    def forge_xhtml(self, mess, mess_xhtml, priv=None, in_reply_to=None):
        """Sending an xhtml message in the room"""

        #The message is created from mess, in case some clients does not support XHTML (xep-0071)
        message = self.forge_message(mess, priv, in_reply_to)
        #We prepare the XHTML node
        if type(mess_xhtml) == unicode:
            mess_xhtml = mess_xhtml.encode("utf8")
        payload = xmpp.simplexml.XML2Node('<body xmlns="%s">%s</body>' % (XML_NAMESPACE, mess_xhtml))
        # We add the XHTML node to the message then send it
        message.addChild('html', {}, [payload], xmpp.NS_XHTML_IM)

        return message
    
    def say(self, *args, **kwargs) :
        """The method to call to make the bot sending messages"""
        #If the bot has not been disabled
        if not self.mute:
            mto, mbody, mtype = self.forge_message(*args, **kwargs)
            self.send_message(mto = mto, mbody = mbody, mtype = mtype)

    def say_xhtml(self, *args, **kwargs) :
        """Method to talk in xhtml"""
        #If the bot has not been disabled
        if not self.mute:
            self.send(self.forge_xhtml(*args, **kwargs))

    def presence(self, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and roles"""
#        if mess.getStatusCode() == u'110':
#            self.name = mess.getFrom().getResource()

        for module in self.modules:
            if isinstance(module, PresenceModule):
                module.do_answer(mess)
        
    def run(self):
        """Method called when the bot is ran"""
        #We start dameons for asynchronous methods
#            except xmpp.protocol.Conflict:
#                msg = _("The ressource defined for the bot in %s is already used" % (self.chatname))
#                logger.error(msg)
#                raise XMPPException(msg)
#
#        #When bot's killed, every asynchronous module must be killed too
#        for module in self.modules:
#            if type(module) == AsyncModule :
#                module.stop()

    def restart(self):
        """ Will ask the manager to restart this room """
        self.manager.restart(self.chatname)

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False

    def iq(self, conn, iqdata) :
        """Method called when the bot receives an IQ message"""
        for module in self.modules:
            if isinstance(module, IQModule):
                module.do_answer(iqdata)
