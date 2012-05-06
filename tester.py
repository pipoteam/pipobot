#!/usr/bin/python2
# -*- coding: utf-8 -*-
import gettext
import logging
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import xmpp

import bot_jabber
import lib
import lib.init_bot


class Tester(bot_jabber.BotJabber):
    def __init__(self):
        # the fake room we will work in
        self.roomname = "unknown@domain.std"
        # informations about the bot itself
        self.nick_bot = "tester"
        self.jid_bot = "bot@botdomain.std"
        bot_jabber.bot_jabber.__init__(self, self.jid_bot, "secret_pwd", self.jid_bot, self.roomname, self.nick_bot)
        self.add_user(self.nick_bot, self.jid_bot)
        #informations about the user we will be using in the fake room
        self.username = "lambda"
        self.jid_frm = "lambda@domain.tld"
        self.add_user(self.username, self.jid_frm)

    def connect(self):
        return True

    def auth(self, node, pwd, resource):
        return True

    def RegisterHandler(self, typ, fct):
        pass

    def send(self, msg):
        if isinstance(msg, xmpp.protocol.Message):
            print msg.getBody()
        else:
            print msg

    def loop(self):
        cmd = ""
        self.add_user("blabla", "blabla@domain.std")
        while cmd != ":q":
            cmd = raw_input(">> ")
            self.fake_msg(cmd)

    def fake_msg(self, body):
        m = xmpp.Message(frm = "%s/%s" % (self.roomname, self.username), 
                         body = body, 
                         to = self.jid_bot,
                         typ = "groupchat")
        self.message(None, m)


    def add_user(self, name, jid, xmpp_client = "mcabber", affiliation = "none", role = "participant"):
        msg_frm = xmpp.JID(jid = "%s/%s" % (self.roomname, name))
        msg = xmpp.Presence(frm = msg_frm, to = self.roomname)
        tag = msg.setTag("x")
        tag.setTag("item")
        tag.setTagAttr("item", "jid", "%s/%s" % (jid, xmpp_client))
        tag.setTagAttr("item", "affiliation", affiliation)
        tag.setTagAttr("item", "role", role)
        self.presence(None, msg)

if __name__ == '__main__':
    # Constants
    DEFAULT_LOG = "/tmp/botjabber.log"
    DEFAULT_XMPPLOG = None #default = no log of xmpp messages
    DEFAULT_LANG = "en"
    APP_NAME = "pipobot"
    DEFAULT_FILENAME = os.path.join(os.path.dirname(globals()["__file__"]),'tester.yml')

    #Parametring options
    parser = lib.init_bot.conf_parser()

    #Reading command-line options
    (options, args) = parser.parse_args()

    #Reading configuration file
    settings_filename, settings = lib.init_bot.read_yml(args, DEFAULT_FILENAME)

    #Configuring logging
    log_filename, logger = lib.init_bot.conf_logging(options.level, settings, APP_NAME, DEFAULT_LOG)
    xmpp_log = settings["config"]["xmpplog"] if "config" in settings and "xmpplog" in settings["config"] else DEFAULT_XMPPLOG

    #Configuring database
    engine = ""
    src = ""
    if "database" in settings:
        engine = settings["database"]["engine"]
        src = settings["database"]["src"]

    logger.info("-- Starting tester of pipobot --")
    logger.info("Reading configuration file : %s" % settings_filename)
    logger.info("Logging file : %s" % log_filename)

    #Configuring language of the application
    lib.init_bot.language(settings, logger, APP_NAME, DEFAULT_LANG)
    sys.path.insert(0,"modules/")

    tester = Tester()

    #Reading command-line options
    (options, args) = parser.parse_args()
    classes_salon = lib.init_bot.read_modules(settings["modules"], settings)
    if engine:
        db_session = lib.init_bot.configure_db(engine, src)
        tester.session = db_session
    tester.add_commands(classes_salon)
    tester.loop()
