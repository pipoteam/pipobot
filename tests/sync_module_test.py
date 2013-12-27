import builtins
import unittest
from pipobot.lib.modules import defaultcmd, SyncModule, Help, answercmd
from base_test import FakeUser, create_test_bot


builtins._ = lambda x: x


class SyncMod(SyncModule):
    def __init__(self, bot):
        desc = "A simple module to test"
        name = "test_sync"
        SyncModule.__init__(self, bot, desc, name)

    @defaultcmd
    def echo(self, sender, message):
        return message

    @answercmd(r"(?P<num>\d+)")
    def num_answer(self, sender, num):
        return "Your number is %d" % int(num)

    @answercmd(r"(?P<arg1>\d+) \+ (?P<arg2>\d+) \=\= (?P<arg3>\d+)")
    def test_answer(self, sender, arg1, arg2, arg3):
        if int(arg1) + int(arg2) == int(arg3):
            return "OK"
        else:
            return "KO"


class SyncModuleTest(unittest.TestCase):
    def setUp(self):
        self.bot = create_test_bot([SyncMod, Help])

    def test_help(self):
        user = FakeUser("bob", self.bot, self)
        user.ask("!help", u'I can execute: \n-test_sync')
        user.ask("!help test_sync", "A simple module to test")

    def test_sync(self):
        user = FakeUser("bob", self.bot, self)
        user.ask("!test_sync some random message", "some random message")
        user.ask(":test_sync 42", "Your number is 42")
        user.ask("!test_sync 1 + 1 == 2", "OK")
        user.ask(":test_sync 1 + 1 == 3", "KO")
