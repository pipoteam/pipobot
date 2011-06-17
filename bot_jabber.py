#!/usr/bin/python
#-*- coding: utf8 -*-

import xmpp
import logging
import sys
import traceback
import threading
import random
import time
logger = logging.getLogger('pipobot.bot_jabber') 


LOG = open('/tmp/botnet7.log', 'a')
XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class bot_jabber(xmpp.Client, threading.Thread):
    def __init__(self, login, passwd, res, chat, name):
        #Obligé de mettre ca pour definir un client...
        self.mute = False
        self.Namespace, self.DBG = 'jabber:client', xmpp.DBG_CLIENT
        jid=xmpp.protocol.JID(login)
        xmpp.Client.__init__(self, jid.getDomain(), debug=[])
        #xmpp.Client.__init__(self, jid.getDomain())
        threading.Thread.__init__(self)
        logger.info("Connexion en cours sur %s" % chat)

        self.name = name
        # dictionnaire stockant la correspondance pseudo <-> login INP-net
        self.jids = {}
        self.droits = {}
        self.alive = True #servira a le tuer
        self.commands_sync = [] #commandes sync a executer
        self.commands_async = [] #commandes async a executer
        self.commands_listen = [] #commandes listen a executer
        self.commands_iq = [] #commandes iq
        self.chat = xmpp.protocol.JID(chat)
        #Connexion jabber, etc...
        con=self.connect()
        if not con:
            print 'Impossible de se connecter !'
            sys.exit()
        auth=self.auth(jid.getNode(), passwd, resource=res)
        if not auth:
            print 'Impossible de s\'authentifier !'
            sys.exit()
        self.RegisterHandler('message', self.message)
        self.RegisterHandler('presence', self.presence)
        self.RegisterHandler('iq', self.iq)

        #Code pour ne pas avoir l'historique
        chatpres = xmpp.protocol.JID(chat+"/"+name)
        p = xmpp.Presence(to=chatpres)
        p.setTag('x', namespace=xmpp.NS_MUC)
        p.getTag('x').addChild('history',{'maxchars':'0'})
        self.send(p)
        self.say("\o/ \o/ Je suis de retour, pour votre plus grand plaisir \o/ \o/ !!!")

    def message(self, conn, mess):
        """Methode appelée lors de la reception d'un message"""

        if self.mute:
            return

        if mess.getSubject() is not None:
            return

        if mess.getTag('delay'):
            return

        m = mess.getBody()
       
        # Commandes listen
        for classe in  self.commands_listen:
            self.answer(classe, mess.getFrom().getResource(), m, mess)

        # Commandes sync
        if m != None:
            m = m.lstrip()
        if m == None or m == "" or (m[0] != '!' and m[0] != ":"):
            return

        cmd = m.split(" ")[0]
        for classe in self.commands_sync:
            rd = random.randint(1, 100)
            if hasattr(classe, 'genericCmd'):
                if cmd in ["!"+s for s in classe.genericCmd]+[":"+s for s in classe.genericCmd]:
                    if mess.getType() == "groupchat" or (mess.getType() == "chat" and classe.pm_allowed):
                        if rd > 3:
                            self.answer(classe, mess.getFrom().getResource(), m.strip(), mess)
                        else:
                            self.say("I'm sorry %s, I'm afraid I can't do that"%(mess.getFrom().getResource()))
            if cmd == "!"+classe.command or cmd == ":"+classe.command:
                if mess.getType() == "groupchat" or (mess.getType() == "chat" and classe.pm_allowed):
                    if rd > 3:
                        self.answer(classe, mess.getFrom().getResource(), m[1+len(classe.command):].strip(), mess)
                    else:
                        self.say("I'm sorry %s, I'm afraid I can't do that"%(mess.getFrom().getResource()))


    def answer(self, classe, sender, m, mess): 
        if sender == self.name:
            return
        if self.mute:
            return
        try:
            send = classe.answer(sender, m)
            if type(send) == str or type(send) == unicode:
                self.say(send, in_reply_to=mess)
            elif type(send) == list:
                for line in send:
                    time.sleep(0.3)
                    self.say(line, in_reply_to=mess)
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
                if send is not None:
                    self.say("Erreur : retour : %s" % send)
        except:
            self.say("Erreur :(")
            logger.error("Erreur dans la commande : %s" % traceback.format_exc())


    def add_commands(self, classes):
        """Methode appellée au debut où l'on spécifie les classes des modules"""

        for classe in classes:
            #print "Ajout de %s" % classe
            objet = classe(self)
            if hasattr(classe, 'answer'):
                if hasattr(objet, 'command'):
                    self.commands_sync.append(objet)
                elif hasattr(objet, 'genericCmd'):
                    self.commands_sync.append(objet)
                else:
                    self.commands_listen.append(objet)
            if hasattr(classe, '_Thread__bootstrap'):
                self.commands_async.append(objet)

    def kill(self):

        self.alive=False
        self.say("Désolé, je me vois dans l'obligation de vous laisser, mais je reviendrai...enfin si on me relance")
        self.disconnect()

    def say(self, mess, priv=None, in_reply_to=None):
        """ Envoi un message sur le salon"""

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
        logger.debug(u"Message envoyé à %s, type %s" % (message.getTo(), message.getType()))


    def say_xhtml(self, mess, mess_xhtml, priv=None, in_reply_to=None):
        """ Envoi un message xhtml sur le salon"""

        # on fait le message de base avec le message pour ceux qui
        # ne supporteraient pas le XHTML (xep-0071)
        if not self.mute:
            message = xmpp.Message(self.chat, mess, typ="groupchat")
            if in_reply_to:
                message.setType( in_reply_to.getType() )
                if in_reply_to.getType() == "chat":
                    message.setTo( in_reply_to.getFrom() )
            if priv:
                message.setTo("%s/%s" % (self.chat, priv))
                message.setType("chat")
            # on prépare le noeud XHTML
            if type(mess_xhtml) == unicode:
                mess_xhtml = mess_xhtml.encode("utf8")
            #mess_xhtml = mess_xhtml.replace("&","&amp;")
            payload=xmpp.simplexml.XML2Node('<body xmlns="%s">%s</body>' % (XML_NAMESPACE, mess_xhtml))
            # On ajoute le noeud au message puis on poste
            message.addChild('html', {}, [payload], xmpp.NS_XHTML_IM)
            self.send(message)

    def presence(self, conn, mess):
        """ Appelé a chaque evenement presence. Sert a mettre à jour la table de correspondance pseudos<->jids """

        for xtag in mess.getTags("x"):
            if xtag.getTag("item"):
                power = xtag.getTag("item").getAttr("role")

        pseudo = mess.getFrom().getResource()
        self.droits[pseudo] = power
        if mess.getType() == 'unavailable':
            try:
                del self.droits[pseudo]
                del self.jids[pseudo]
            except KeyError:
                print "Sortie sans être entré Oo"
            return

        if mess.getJid() is None:
            print "Bot non admin"
            return

        jid = mess.getJid().split('/')[0]
        self.jids[pseudo] = jid

        
    def run(self):
        for classe in self.commands_async:
            classe.daemon = True
            classe.start()

        while self.alive:
            self.Process(1)

        for classe in self.commands_async:
            classe.stop()
    def jid2pseudo(self, jid):
        for k,v in self.jids.iteritems():
            if v == jid:
                return k
        return jid

    def pseudo2jid(self, pseudo):
        return self.jids[pseudo]

    def pseudo2role(self, pseudo):
        return self.droits[pseudo]
        
    def disableMute(self):
        self.mute = False

    def iq(self, conn, iqdata) :
        """ Appelé lorsque l'on recoit un iq """

        for classe in  self.commands_iq :
            classe.process(iqdata)
