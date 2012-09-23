# -*- coding: utf-8 -*-
import logging
import re
import traceback
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
        return self.bot.create_msg(user, input_msg)

    def assertRegexpListMatches(self, bot_rep, expected_re):
        expected = map(re.compile, expected_re)
        regex = expected[0]
        i = 0

        while not regex.match(bot_rep) and i < len(expected):
            i += 1
            regex = expected[i]

        if i == len(expected):
            raise AssertionError(_("No regexp from %s matches %s") % (expected_re, bot_rep))
