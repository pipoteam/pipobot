# -*- coding: utf-8 -*-
import queue
import random
import re
import string
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pipobot.bot_test import TestBot
from pipobot.lib.bdd import Base

import builtins
builtins._ = lambda x: x


def create_test_bot(mods):
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return TestBot("pipotest", "login", CHAN, mods, session, queue.Queue())


class ModuleTest(unittest.TestCase):
    __usable = False

    def __init__(self, methodName='runTest', bot=None, cmds=[]):
        unittest.TestCase.__init__(self, methodName)
        if bot is None:
            bot = create_test_bot(cmds)
        self.bot = bot

    def bot_answer(self, input_msg, user="test"):
        th = self.bot.create_msg(user, input_msg)
        th.join()
        return self.bot.output.get()

    def assertRegexpListMatches(self, bot_rep, expected_re):
        expected = list(map(re.compile, expected_re))
        regex = expected[0]
        i = 0

        while not regex.match(bot_rep) and i < len(expected) - 1:
            i += 1
            regex = expected[i]

        if i == len(expected) - 1:
            raise AssertionError(_("No regexp from %s matches %s") % (expected_re, bot_rep))

def string_gen(size):
    return "".join([random.choice(string.ascii_lowercase) for i in range(size)])


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

