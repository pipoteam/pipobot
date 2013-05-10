#!/usr/bin/python
#-*- coding: utf-8 -*-
"""This module contains a class to test the bot in a CLI mode"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import logging
import random
from pipobot.bot_test import TestBot, ForgedMsg
from pipobot.lib.utils import color


logger = logging.getLogger('pipobot.bot_jabber')
nickname_colors = ["blue", "cyan", "red", "purple", "yellow"]
nickname_colors.extend(["bright %s" % col for col in nickname_colors])


class MultiClientEcho(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.username = ""
        self.jid = ""
        self.role = ""
        self.color = random.choice(nickname_colors)

    def connectionMade(self):
        self.factory.clients.append(self)
        self.transport.write("Bienvenue !\n")

    def dataReceived(self, data):
        if not self.username:
            username, jid, role = data.strip().split(";")
            self.factory.bot.users.add_user(username, jid, role, self.factory.bot.chatname)
            print "%s joined : jid=%s; role=%s" % (username, jid, role)
            self.username = username
            self.jid = jid
            self.role = role
            msg = "*** %s has joined\n" % username
        else:
            msg = "%s %s\n" % (color("<%s>" % self.username, self.color),
                               data.strip())

            msg += "%s %s\n" % (color("<%s>" % self.factory.bot.name, self.factory.bot.color),
                                self.factory.bot.create_msg(self.username, data.strip()))

        #Broadcast message to all clients + bot answer
        for client in self.factory.clients:
            client.transport.write(msg.encode("utf-8"))

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        for client in self.factory.clients:
            client.transport.write("*** %s has left\n" % self.username)
        self.factory.bot.users.rm_user(self.username)


class MultiClientEchoFactory(Factory):
    def __init__(self, bot):
        self.bot = bot
        self.clients = []

    def buildProtocol(self, addr):
        return MultiClientEcho(self)


class TwistedBot(TestBot):
    def __init__(self, name, login, chatname, modules, session):
        TestBot.__init__(self, name, login, chatname, modules, session)
        self.client_facto = MultiClientEchoFactory(self)
        self.color = random.choice(nickname_colors)

        # Have to disable this error in pylint, why ?
        # pylint: disable=E1101
        reactor.listenTCP(8123, self.client_facto)
        reactor.run()
        # pylint: enable=E1101

    def say(self, *args, **kwargs):
        ret = []
        args = args[0]
        if args is not None:
            ret = self.decode_module_message(args)
            msg = "%s %s\n" % (color("<%s>" % self.name, self.color), ret)

            for client in self.client_facto.clients:
                client.transport.write(msg.encode("utf-8"))
