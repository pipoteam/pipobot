# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pipobot.bot_test import TestBot
from pipobot.lib.bdd import Base
import queue


DOMAIN = "domain.tld"
CHAN = "test@%s" % DOMAIN


class FakeUser:
    def __init__(self, name, bot, tester, jid=None, role="moderator", chan=CHAN):
        self.name = name
        self.bot = bot
        if jid is None:
            jid = "%s@%s" % (name, DOMAIN)
        self.jid = jid
        self.role = role
        self.chan = chan
        self.tester = tester
        self.bot.occupants.add_user(name, jid, role)

    def ask(self, msg, expected):
        ret = self.bot.create_msg(self.name, msg)
        ret.join()
        ret = self.bot.output.get()
        self.tester.assertEqual(ret, expected)

    def change_nick(self, new_nick):
        self.bot.users.rm_user(self.name)
        self.name = new_nick
        self.bot.occupants.add_user(new_nick, self.jid, self.role)

    def leave(self):
        self.bot.users.rm_user(self.name)

def create_test_bot(mods):
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return TestBot("pipotest", "login", CHAN, mods, session, queue.Queue())
