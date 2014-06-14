import random
import datetime
import time
import unittest
import pipobot.lib.parsedates as parsedates


def eq(d1, d2):
    return time.mktime(d1) == time.mktime(d2)


class TestParseDates(unittest.TestCase):
    def test_parser(self):
        for d in ("18/01/12", "18/01/2012"):
            ret = parsedates.parseall(d)
            self.assertTrue(eq(ret,
                            datetime.datetime(2012, 1, 18).timetuple()))

        for i in range(5):
            delta = random.randint(1, 1000)
            d = "J+%s" % delta
            ret = parsedates.parseall(d)
            today = datetime.datetime.now()
            expected = (today+datetime.timedelta(days=delta)).timetuple()
            self.assertTrue(eq(ret,
                            expected))


        for i in range(5):
            delta = random.randint(1, 23)
            d = "H+%s" % delta
            ret = parsedates.parseall(d)
            today = datetime.datetime.now()
            expected = (today+datetime.timedelta(hours=delta)).timetuple()
            self.assertTrue(eq(ret,
                            expected))

        for i in range(5):
            delta = random.randint(1, 23)
            d = "M+%s" % delta
            ret = parsedates.parseall(d)
            today = datetime.datetime.now()
            expected = (today+datetime.timedelta(minutes=delta)).timetuple()
            self.assertTrue(eq(ret,
                            expected))

        hours = ["18h00", "18h", "18H"]
        for d in hours:
            now = datetime.datetime.now()
            ret = parsedates.parseall(d)
            self.assertTrue(eq(datetime.datetime(now.year, now.month, now.day,
                                                 18, 00).timetuple(),
                               ret))


        d = "18/01/12,18h10"
        ret = parsedates.parseall(d)
        self.assertTrue(eq(ret,
                        datetime.datetime(2012, 1, 18, 18, 10).timetuple()))


        d = "J+1,18h02"
        ret = parsedates.parseall(d)
        today = datetime.datetime.now()
        tomorrow = (today+datetime.timedelta(days=1))
        expected = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 18, 2).timetuple()
        self.assertTrue(eq(ret, expected))

        d = "J+1,H+1"
        ret = parsedates.parseall(d)
        today = datetime.datetime.now()
        tomorrow = (today+datetime.timedelta(days=1, hours=1))
        expected = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, tomorrow.hour, tomorrow.minute).timetuple()
        self.assertTrue(eq(ret, expected))


        errs = ["J+1,p+1", "p+1,", "J+1,pipo", "+pipo", "pipo", "J+", "M+1,pipo", "pipo,J+1"]
        for d in errs:
            self.assertRaises(parsedates.ParseExcept, parsedates.parseall, d)
