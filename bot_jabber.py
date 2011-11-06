#!/usr/bin/python
#-*- coding: utf8 -*-
"""This file contains the class 'bot_jabber' wich is a bot for jabber MUC"""

import xmpp
import logging
import sys
import traceback
import threading
import time
from lib.modules import ListenModule, AsyncModule, MultiSyncModule, SyncModule
logger = logging.getLogger('pipobot.bot_jabber') 


XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class bot_jabber(xmpp.Client, threading.Thread):
    """The implementation of a bot for jabber MUC"""
    
    def __init__(self, login, passwd, res, chat, name, xmpp_log = None):

        #Definition of an XMPP client
        self.Namespace, self.DBG = 'jabber:client', xmpp.DBG_CLIENT

        jid = xmpp.protocol.JID(login)
        if xmpp_log is not None:
            f = open(xmpp_log, "a")
            xmpp.Client.__init__(self, jid.getDomain(), debug=f)
            self._DEBUG._fh = f
        else:
            xmpp.Client.__init__(self, jid.getDomain(), debug = [])
        threading.Thread.__init__(self)

        logger.info(_("Connecting to %s") % chat)
        #Connecting
        con = self.connect()
        if not con:
            logger.error(_("Unable to connect !"))
            sys.exit()
        auth = self.auth(jid.getNode(), passwd, resource=res)
        if not auth:
            logger.error(_("Unable to authenticate !"))
            sys.exit()
        self.modules = []
        self.mute = False
        self.alive = True 
        self.name = name

        self.chat = xmpp.protocol.JID(chat)

        self.jids = {}
        self.droits = {}

        self.RegisterHandler('message', self.message)
        self.RegisterHandler('presence', self.presence)
        #self.RegisterHandler('iq', self.iq)

        #To avoid getting the history of messages when connecting
        chatpres = xmpp.protocol.JID(chat+"/"+name)
        pres = xmpp.Presence(to=chatpres)
        pres.setTag('x', namespace=xmpp.NS_MUC)
        pres.getTag('x').addChild('history', {'maxchars':'0'})
        self.send(pres)

        self.say(_("Hello everyone !"))

    def message(self, conn, mess):
        """Method called when the bot receives a message"""

        if self.mute                         \
           or mess.getSubject() is not None  \
           or mess.getTag('delay')           \
           or mess.getBody() == None :
                return

        msg_body = mess.getBody().lstrip()
        logger.info(self.modules)
        for module in self.modules :
            #module.answer(classe, mess.getFrom().getResource(), msg_body, mess)
            module.answer(mess.getFrom().getResource(), msg_body, mess)

    def add_commands(self, classes):
        """Method called when we specify modules' classes, at the creation of bot's instance"""

        for classe in classes:
            objet = classe(self)
            self.modules.append(objet)

    def kill(self):
        """Method used to kill the bot"""

        self.alive = False
        self.say(_("I've been asked to leave you"))
        self.disconnect()

    def forge_message(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        message = xmpp.Message(self.chat, mess, typ="groupchat")
        if in_reply_to:
            message.setType( in_reply_to.getType() )
            if in_reply_to.getType() == "chat":
                message.setTo( in_reply_to.getFrom() )
        if priv:
            message.setTo("%s/%s" % (self.chat, priv))
            message.setType("chat")

        return message


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
        #If the bot has not been disabled
        if not self.mute:
            self.send(self.forge_message(*args, **kwargs))

    def say_xhtml(self, *args, **kwargs) :
        #If the bot has not been disabled
        if not self.mute:
            self.send(self.xhtml(*args, **kwargs))

    def presence(self, conn, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and rights"""
        power = "unknown" 

        #Get the role of the participant
        for xtag in mess.getTags("x"):
            if xtag.getTag("item"):
                power = xtag.getTag("item").getAttr("role")

        pseudo = mess.getFrom().getResource()
        
        #The user [pseudo] leaves the room
        if mess.getType() == 'unavailable':
            try:
                del self.droits[pseudo]
                del self.jids[pseudo]
            except KeyError:
                logger.error(_("User %s leaves without being in the room !") % (pseudo))
            return

        self.droits[pseudo] = power

        #If the bot has no rights to view user's JID
        if mess.getJid() is None:
            logger.error(_("I can't read JID in this room !"))
            return

        jid = mess.getJid().split('/')[0]
        self.jids[pseudo] = jid

        
    def run(self):
        """Method called when the bot is ran"""
        #We start dameons for asynchronous methods
        for module in self.modules:
            if type(module) == AsyncModule :
                module.start()
        
        #client's loop, exited only when self.alive has been set to False
        while self.alive:
            self.Process(1)

        #When bot's killed, every asynchronous module must be killed too
        for module in self.modules:
            if type(module) == AsyncModule :
                classe.stop()

    def jid2pseudo(self, jid):
        """Method used to return pseudo from JID"""
        for jids, pseudo in self.jids.iteritems():
            if jids == jid:
                return pseudo
        return jid

    def pseudo2jid(self, pseudo):
        """Method used to return JID from pseudo"""
        try:
            return self.jids[pseudo]
        except KeyError:
            logger.error(_("The user %s is not in the room !") % (pseudo))
            return _("unknown user %s") % (pseudo)

    def pseudo2role(self, pseudo):
        """Method used to get role of a pseudo"""
        try:
            return self.droits[pseudo]
        except KeyError:
            logger.error(_("The user %s is not in the room !") % (pseudo))
            return _("unknown user %s") % (pseudo)
        
    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False

    def iq(self, conn, iqdata) :
        """Method called when the bot receives an IQ message"""

        # WON'T WORK WITH NEW MODULES, TO BE CORRECTED
        for classe in  self.commands_iq :
            classe.process(iqdata)
