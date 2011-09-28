#!/usr/bin/python
#-*- coding: utf8 -*-
"""This file contains the class 'bot_jabber' wich is a bot for jabber MUC"""

import xmpp
import logging
import sys
import traceback
import threading
import time
logger = logging.getLogger('pipobot.bot_jabber') 


XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class bot_jabber(xmpp.Client, threading.Thread):
    """The implementation of a bot for jabber MUC"""
    def __init__(self, login, passwd, res, chat, name):
        self.mute = False
        #Definition of an XMPP client
        self.Namespace, self.DBG = 'jabber:client', xmpp.DBG_CLIENT
        jid = xmpp.protocol.JID(login)
        xmpp.Client.__init__(self, jid.getDomain(), debug=[])
        threading.Thread.__init__(self)
        logger.info(_("Connecting to %s") % chat)

        self.name = name
        #pseudo <-> jid
        self.jids = {}
        #pseudo <-> rights on the channel
        self.droits = {}
        #If set to False, the bot will be killed
        self.alive = True 
        #synchronous commands
        self.commands_sync = [] 
        #asynchronous commands
        self.commands_async = []
        #listening commands
        self.commands_listen = []
        #iq commands
        self.commands_iq = []
        self.chat = xmpp.protocol.JID(chat)
        #Connecting
        con = self.connect()
        if not con:
            logger.error(_("Unable to connect !"))
            sys.exit()
        auth = self.auth(jid.getNode(), passwd, resource=res)
        if not auth:
            logger.error(_("Unable to authenticate !"))
            sys.exit()
        self.RegisterHandler('message', self.message)
        self.RegisterHandler('presence', self.presence)
        self.RegisterHandler('iq', self.iq)

        #To avoid getting the history of messages when connecting
        chatpres = xmpp.protocol.JID(chat+"/"+name)
        pres = xmpp.Presence(to=chatpres)
        pres.setTag('x', namespace=xmpp.NS_MUC)
        pres.getTag('x').addChild('history', {'maxchars':'0'})
        self.send(pres)
        self.say(_("Hello everyone !"))

    def message(self, conn, mess):
        """Method called when the bot receives a message"""

        if self.mute:
            return

        if mess.getSubject() is not None:
            return

        if mess.getTag('delay'):
            return

        msg_body = mess.getBody()
        if msg_body == None:
            return
       
        # listen commands
        for classe in  self.commands_listen:
            self.answer(classe, mess.getFrom().getResource(), msg_body, mess)

        msg_body = msg_body.lstrip()
        if msg_body == "" or (msg_body[0] != '!' and msg_body[0] != ":"):
            return

        # Synchronous commands
        cmd = msg_body.split(" ")[0]
        for classe in self.commands_sync:
            if hasattr(classe, 'genericCmd'):
                test = cmd[1:] in classe.genericCmd
                tosend = msg_body
            else:
                test = cmd[1:] == classe.command
                tosend = msg_body[1+len(classe.command):]

            if test and (mess.getType() == "groupchat" or 
                         (mess.getType() == "chat" and classe.pm_allowed)):
                self.answer(classe, mess.getFrom().getResource(), tosend.strip(), mess)

    def answer(self, classe, sender, text_msg, mess): 
        """Method used to dispatch a command to the appropriate module"""
        #The bot does not ansers to itself
        if sender == self.name:
            return

        #If the bot has been muted
        if self.mute:
            return
        try:
            #Calling the 'answer" method of the module
            send = classe.answer(sender, text_msg)
            #If the method is just a string, it will be the bot's answer
            if type(send) == str or type(send) == unicode:
                self.say(send, in_reply_to=mess)
            #If it's a list we display each message with a time delay
            elif type(send) == list:
                for line in send:
                    time.sleep(0.3)
                    self.say(line, in_reply_to=mess)
            #If it's a dictionary, it is {"text": raw_message, "xhtml" : xhtml_message}
            #or                          {"text": raw_message, "monospace" : True}
            #so xhtml message will be raw_message with xhtml information to have monospaced text
            elif type(send) == dict:
                if "xhtml" in send and "text" in send:
                    self.say_xhtml(send["text"], send["xhtml"], in_reply_to=mess)
                elif "text" in send and "monospace" in send:
                    if send[monospace]:
                        html_msg = '<p><span style="font-family: monospace">%s</span></p>' % send["text"].replace("\n", "<br/>\n") 
                        self.say_xhtml(send["text"], html_msg, in_reply_to=mess)
                    else:
                        self.say(send["text"], in_reply_to = mess)
                        
            elif type(send) == tuple and len(send) >= 2:
                if send[1] is None:
                    self.say(send[0], in_reply_to=mess)
                else:
                    self.say_xhtml(send[0], send[1], in_reply_to=mess)
                if len(send) == 3 and type(send[2]) == dict:
                    for user, message in send[2].iteritems():
                        if type(message) == str or type(message) == unicode:
                            self.say(message, priv=user, in_reply_to=mess)
                        elif type(message) == tuple and len(message) >= 2:
                            if message[1] is None:
                                self.say(message[1], priv=user, in_reply_to=mess)
                            else:
                                self.say_xhtml(message[0], message[1], priv=user, in_reply_to=mess)

            else:
                #In any other case, an error has occured in the module
                if send is not None:
                    self.say(_("Error from module %s : %s") % (classe.command, send))
        except:
            self.say(_("Error !"))
            logger.error(_("Error from module %s : %s") % (classe.command, traceback.format_exc()))


    def add_commands(self, classes):
        """Method called when we specify modules' classes, at the creation of bot's instance"""
        for classe in classes:
            objet = classe(self)
            if hasattr(classe, 'answer'):
                if hasattr(objet, 'command') or hasattr(objet, 'genericCmd'):
                    self.commands_sync.append(objet)
                else:
                    self.commands_listen.append(objet)
            if hasattr(classe, '_Thread__bootstrap'):
                self.commands_async.append(objet)

    def kill(self):
        """Method used to kill the bot"""
        self.alive = False
        self.say(_("I've been asked to leave you"))
        self.disconnect()

    def say(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        #If the bot has not been disabled
        if not self.mute:
            message = xmpp.Message(self.chat, mess, typ="groupchat")
            if in_reply_to:
                message.setType( in_reply_to.getType() )
                if in_reply_to.getType() == "chat":
                    message.setTo( in_reply_to.getFrom() )
            #priv overrides in_reply_to
            if priv:
                message.setTo("%s/%s" % (self.chat, priv))
                message.setType("chat")
            self.send(message)
            logger.debug(_("Message sent to %s, type %s") % (message.getTo(), message.getType()))


    def say_xhtml(self, mess, mess_xhtml, priv=None, in_reply_to=None):
        """Sending an xhtml message in the room"""
        #The message is created from mess, in case some clients does not support XHTML (xep-0071)

        #If the bot has not been disabled
        if not self.mute:
            message = xmpp.Message(self.chat, mess, typ="groupchat")
            if in_reply_to:
                message.setType( in_reply_to.getType() )
                if in_reply_to.getType() == "chat":
                    message.setTo( in_reply_to.getFrom() )
            #In case this is a private message
            if priv:
                message.setTo("%s/%s" % (self.chat, priv))
                message.setType("chat")
            #We prepare the XHTML node
            if type(mess_xhtml) == unicode:
                mess_xhtml = mess_xhtml.encode("utf8")
            payload = xmpp.simplexml.XML2Node('<body xmlns="%s">%s</body>' % (XML_NAMESPACE, mess_xhtml))
            # We add the XHTML node to the message then send it
            message.addChild('html', {}, [payload], xmpp.NS_XHTML_IM)
            self.send(message)

    def presence(self, conn, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and rights"""
        power = "" 

        #Get the role of the participant
        for xtag in mess.getTags("x"):
            if xtag.getTag("item"):
                power = xtag.getTag("item").getAttr("role")

        if power == "":
            power = "unknown"
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
        for classe in self.commands_async:
            classe.daemon = True
            classe.start()
        
        #client's loop, exited only when self.alive has been set to False
        while self.alive:
            self.Process(1)

        #When bot's killed, every asynchronous module must be killed too
        for classe in self.commands_async:
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
        for classe in  self.commands_iq :
            classe.process(iqdata)
