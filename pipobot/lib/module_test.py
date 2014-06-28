# -*- coding: utf-8 -*-
import random
import re
import string
import unittest


class ModuleTest(unittest.TestCase):
    __usable = False

    def __init__(self, methodName='runTest', bot=None):
        unittest.TestCase.__init__(self, methodName)
        self.bot = bot

    @staticmethod
    def parametrize(testcase_class, bot):
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_class)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_class(name, bot))
        return suite

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

        if i == len(expected):
            raise AssertionError(_("No regexp from %s matches %s") % (expected_re, bot_rep))

def string_gen(size):
    return "".join([random.choice(string.ascii_lowercase) for i in range(size)])
