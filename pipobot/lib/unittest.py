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


class UnitType:
    EXACT = "exact_test"
    RE = "re_test"
    EXCEPT = "except_test"


def color(txt, color_name):
    return "\033[%sm%s\033[0m" % (color_codes[color_name], txt)


class UnitTest:
    __usable = False
    EXACT = "exact_test"
    RE = "re_test"
    EXCEPT = "except_test"

    def __init__(self, commands, bot, module):
        self.bot = bot
        self.commands = commands
        self.module = module

    def gen_report(self, error, msg, description):
        colored_res = color("[KO]", "red") if error else color("[OK]", "green")
        report = u"%s %s" % (colored_res, description)
        if msg != "":
            report += u" → %s" % msg
        return report

    def test_all(self):
        print "Tests du module %s" % color(self.module, "cyan")
        for (command, params) in self.commands:
            if "pre_hook" in params:
                params["pre_hook"]()
            print self.test(command, params)
            if "post_hook" in params:
                params["post_hook"]()

    def test(self, command, params):
        try:
            do_test = getattr(self, params["type"])
            if "sender" not in params:
                params["sender"] = "pipo"
            logger.debug(command)
            res = self.bot.create_msg(params["sender"], command)
            logger.debug(res)
            error, msg = do_test(res, params)
        except:
            exc = traceback.format_exc().decode("utf-8")
            error = True
            msg = u"Exception raised : %s" % exc

        return self.gen_report(error, msg, params["desc"])

    def exact_test(self, res, params):
        expected = params["expected"] if type(params["expected"]) == list else [params["expected"]]
        if res not in params["expected"]:
            return True, u"Expected “%s”, found “%s”" % (expected,
                                                         res)
        else:
            return False, ""

    def re_test(self, res, params):
        regexps = params["expected"] if type(params["expected"]) == list else [params["expected"]]
        regexps = map(re.compile, regexps)
        tst = any(regexp.match(res) for regexp in regexps)
        if tst:
            return False, ""
        else:
            expect = ", ".join(map(lambda reg: getattr(reg, "pattern"),
                                   regexps))
            return True, (u"Expected result matching one of the patterns “%s”, "
                          u"found “%s”") % (expect, res)

    def except_test(self, res, params):
        error = (res in ["Error!", ""])
        msg = "Error returned in the module !!" if error else ""
        return error, msg
