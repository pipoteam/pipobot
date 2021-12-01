import unittest

from pipobot.lib.modules import SyncModule, Help
from pipobot.lib.module_test import create_test_bot, FakeUser
from listen_module_test import ListenMod, ListenMod2


class SyncMod(SyncModule):
    def __init__(self, bot):
        SyncModule.__init__(self, bot, "pipo", "pipo")

class SyncMod2(SyncModule):
    def __init__(self, bot):
        SyncModule.__init__(self, bot, "pouet", "pouet")

class SyncMod3(SyncModule):
    def __init__(self, bot):
        SyncModule.__init__(self, bot, "qsdf", "qsdf")

class HelpTest(unittest.TestCase):
    def setUp(self):
        self.bot = create_test_bot([ListenMod, ListenMod2, SyncMod,
                                    SyncMod2, SyncMod3, Help])

    def test_help(self):
        user = FakeUser("bob", self.bot, self)
        ret = self.bot.create_msg(user.name, "!help all")
        ret.join()

        answer = self.bot.output.get()

        for mod in ("pipo", "pouet", "qsdf", "test_listen2"):
            self.assertIn(mod, answer)
