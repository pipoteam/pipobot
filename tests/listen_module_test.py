import unittest
from pipobot.lib.modules import Help, ListenModule
from pipobot.lib.module_test import FakeUser, create_test_bot


class ListenMod(ListenModule):
    def __init__(self, bot):
        desc = "A simple listen module"
        name = "test_listen"
        ListenModule.__init__(self, bot, name, desc)

    def answer(self, sender, message):
        return "Answer"


class ListenMod2(ListenModule):
    def __init__(self, bot):
        desc = "A simple listen module"
        name = "test_listen2"
        ListenModule.__init__(self, bot, name, desc)

    def answer(self, sender, message):
        if sender == "bob":
            return "Answer2"


class ListenModuleTest(unittest.TestCase):
    def setUp(self):
        self.bot = create_test_bot([ListenMod, ListenMod2, Help])

    def test_listen(self):
        user = FakeUser("bob", self.bot, self)
        user.ask("pipo !", 'Answer\nAnswer2')

        user = FakeUser("pipo", self.bot, self)
        user.ask("pipo !", 'Answer')

        user = FakeUser("pipotest", self.bot, self)
        user.ask("pipo !", "")

        user = FakeUser("plop", self.bot, self)
        user.ask("!help test_listen", "A simple listen module")
