import time
import unittest
from pipobot.lib.modules import Help, AsyncModule
from pipobot.lib.module_test import FakeUser, create_test_bot


MODULE_DELAY = 3

class AsyncMod(AsyncModule):
    def __init__(self, bot):
        desc = "A simple async module"
        name = "test_async"
        AsyncModule.__init__(self, bot, name, desc, delay=MODULE_DELAY)

    def action(self):
        self.bot.say(time.time())


class AsyncModuleTest(unittest.TestCase):
    def setUp(self):
        self.bot = create_test_bot([AsyncMod, Help])

    def test_async(self):
        t = time.time()
        result = self.bot.output.get()
        self.assertEquals(int(result - t), MODULE_DELAY)

        t = time.time()
        result = self.bot.output.get()
        self.assertEquals(int(result - t), MODULE_DELAY)
