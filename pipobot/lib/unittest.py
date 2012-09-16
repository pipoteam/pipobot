# -*- coding: utf-8 -*-
import logging
import re
import traceback

logger = logging.getLogger("pipobot.unittest")

color_codes = {
    'black':     '0;30',     'bright gray':   '0;37',
    'blue':      '0;34',     'white':         '1;37',
    'green':     '0;32',     'bright blue':   '1;34',
    'cyan':      '0;36',     'bright green':  '1;32',
    'red':       '0;31',     'bright cyan':   '1;36',
    'purple':    '0;35',     'bright red':    '1;31',
    'yellow':    '0;33',     'bright purple': '1;35',
    'dark gray': '1;30',     'bright yellow': '1;33',
    'normal':   '0'
}


def color(txt, color_name):
    return "\033[%sm%s\033[0m" % (color_codes[color_name], txt)

class UnitTest:
    __usable = False

    def __init__(self, cmd, desc=None, sender="test", pre_hook=None, post_hook=None):
        self.cmd = cmd
        self.desc = desc if desc is not None else "Testing %s" % cmd
        self.sender = sender
        self.pre_hook = pre_hook
        self.post_hook = post_hook

    @staticmethod
    def gen_report(error, msg, description):
        colored_res = color("[KO]", "red") if error else color("[OK]", "green")
        report = u"%s %s" % (colored_res, description)
        if msg != "":
            report += u" → %s" % msg
        return report

    def test(self, bot):
        if self.pre_hook is not None:
            self.pre_hook()
        logger.debug(self.cmd)
        res = bot.create_msg(self.sender, self.cmd)
        logger.debug(res)
        error, msg = self.check_test(res)
        print self.gen_report(error, msg, self.desc)
        if self.post_hook is not None:
            self.post_hook()
        return self.gen_report(error, msg, self.desc)

class ReTest(UnitTest):
    __usable = False

    def __init__(self, cmd, expected, desc=None, sender='test', pre_hook=None, post_hook=None):
        UnitTest.__init__(self, cmd, desc, sender, pre_hook, post_hook)
        expected = expected if type(expected) is list else [expected]
        self.regexps = map(re.compile, expected)

    def check_test(self, res):
        tst = any(regexp.match(res) for regexp in self.regexps)
        if tst:
            return False, ""
        else:
            expect = ", ".join(map(lambda reg: getattr(reg, "pattern"),
                                   self.regexps))
            return True, (u"Expected result matching one of the patterns “%s”, "
                          u"found “%s”") % (expect, res)

class ExactTest(UnitTest):
    __usable = False

    def __init__(self, cmd, expected, desc=None, sender='test', pre_hook=None, post_hook=None):
        UnitTest.__init__(self, cmd, desc, sender, pre_hook, post_hook)
        self.expected = expected if type(expected) is list else [expected]

    def check_test(self, res):
        tst = res in self.expected
        if tst:
            return False, ""
        else:
            expect = ", ".join(self.expected)
            return True, (u"Expected result should be in  “%s”, "
                          u"but found “%s”") % (expect, res)

class ExceptTest(UnitTest):
    __usable = False

    def check_test(self, res):
        error = (res in ["Error!", "", None])
        msg = "Error returned in the module !!" if error else ""
        return error, msg


class GroupUnitTest:
    __usable = False
    def __init__(self, tests, bot, module):
        self.bot = bot
        self.tests = tests
        self.module = module

    def test_all(self):
        print "Tests du module %s" % color(self.module, "cyan")
        for unit_test in self.tests:
            unit_test.test(self.bot)
