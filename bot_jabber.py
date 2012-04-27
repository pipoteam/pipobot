#!/usr/bin/python
#-*- coding: utf8 -*-
"""This file contains the class 'bot_jabber' wich is a bot for jabber MUC"""

import logging
import threading
import xmpp
import xml.parsers.expat
from lib.modules import AsyncModule, PresenceModule, IQModule
from lib.user import Occupants
logger = logging.getLogger('pipobot.bot_jabber') 

class XMPPException(Exception):
    """ For errors due to XMPP (conflict, connection/authentification failed, …) """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class bot_jabber(xmpp.Client, threading.Thread):
    """The implementation of a bot for jabber MUC"""
    
    def __init__(self, login, passwd, res, chat, name, xmpp_log = None, manager = None):
        self.chatname = chat
        self.manager = manager

        #Definition of an XMPP client
        self.Namespace, self.DBG = 'jabber:client', xmpp.DBG_CLIENT

        jid = xmpp.protocol.JID(login)

        if xmpp_log is not None:
            #Write all XMPP messages seen by the bot to a log file
            f = open(xmpp_log, "a")
            xmpp.Client.__init__(self, jid.getDomain(), debug=f)
            self._DEBUG._fh = f
        else:
            #No debug
            xmpp.Client.__init__(self, jid.getDomain(), debug = [])
        threading.Thread.__init__(self)

        logger.info(_("Connecting to %s") % chat)
        #Connecting
        con = self.connect()
        if not con:
            logger.error(_("Unable to connect !"))
            raise XMPPException(_("Unable to connect !"))
        #Authenticating
        auth = self.auth(jid.getNode(), passwd, resource=res)
        if not auth:
            logger.error(_("Unable to authenticate !"))
            raise XMPPException(_("Unable to authenticate !"))

        self.modules = []

        #If set to True, the bot will not be able to send messages
        self.mute = False
        self.alive = True 
        
        #The nickname the bot will use to join rooms
        #This nickname will be set by the reception of a presence message after joining the room
#        self.name = ""
        self.name = name

        #The room the bot will join
        self.chat = xmpp.protocol.JID(chat)
        
        #We will stock in it informations about users that join/leave
        self.occupants = Occupants()

        #xmpppy handlers to XMPP stanzas
        self.RegisterHandler('message', self.message)
        self.RegisterHandler('presence', self.presence)
        self.RegisterHandler('iq', self.iq)

        #Joins the room : sends initial presence
        chatpres = xmpp.protocol.JID(chat+"/"+name)
        pres = xmpp.Presence(to=chatpres)
        pres.setTag('x', namespace=xmpp.NS_MUC)
        #To avoid getting the history of messages when connecting
        pres.getTag('x').addChild('history', {'maxchars':'0'})
        self.send(pres)
        
        #Saying hello to the room !
        self.say(_("Hello everyone !"))

    def message(self, conn, mess):
        """Method called when the bot receives a message"""
        #We ignore messages in some cases : 
        #   - it has a subject (change of room topic for instance)
        #   - it is a 'delay' message (backlog at room join)
        #   - the message is empty
        if self.mute                         \
           or mess.getSubject() is not None  \
           or mess.getTag('delay')           \
           or mess.getBody() == None :
                return
        
        #We look for a module which is concerned by the message
        for module in self.modules :
            if not isinstance(module, PresenceModule):
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
        self.say(_("I've been asked to leave you"))
        #The bot leaves the room
        logger.info("Killing %s" % self.chatname)
        try:
            self.disconnect()
        except xml.parsers.expat.ExpatError:
            pass

    def forge_message(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        message = xmpp.Message(self.chat, mess, typ="groupchat")
        if in_reply_to:
            message.setType( in_reply_to.getType() )
            if in_reply_to.getType() == "chat":
                message.setTo( in_reply_to.getFrom() )

        #If the bot answers in private
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
        """The method to call to make the bot sending messages"""
        #If the bot has not been disabled
        if not self.mute:
            self.send(self.forge_message(*args, **kwargs))

    def say_xhtml(self, *args, **kwargs) :
        """Method to talk in xhtml"""
        #If the bot has not been disabled
        if not self.mute:
            self.send(self.forge_xhtml(*args, **kwargs))

    def presence(self, conn, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and roles"""
        if mess.getStatusCode() == u'110':
            self.name = mess.getFrom().getResource()

        for module in self.modules:
            if isinstance(module, PresenceModule):
                module.do_answer(mess)
        
    def run(self):
        """Method called when the bot is ran"""
        #We start dameons for asynchronous methods
        for module in self.modules:
            if isinstance(module, AsyncModule):
                module.start()
        
        #client's loop, exited only when self.alive has been set to False
        while self.alive:
            try:
                self.Process(1)
            except xmpp.protocol.Conflict:
                msg = _("The ressource defined for the bot in %s is already used" % (self.chatname))
                logger.error(msg)
                raise XMPPException(msg)

        #When bot's killed, every asynchronous module must be killed too
        for module in self.modules:
            if type(module) == AsyncModule :
                module.stop()

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
