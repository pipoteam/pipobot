#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import threading, traceback
import time
from model import Remind
import lib.modules.AsyncModule


class AsyncReminder(lib.modules.AsyncModule):
    def __init__(self, bot):
        desc = "Display reminds !"
        lib.modules.AsyncModule.__init__(bot, 
                                        name = "remind_check",
                                        desc = desc)
        self.lastcheck = time.time()

    def action(self):
        reminds = self.bot.session.query(Remind).order_by(Remind.date).all()
        now = time.time()
        for remind in reminds:
            if remind.date >= self.lastcheck and remind.date < now:
                date = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(remind.date)))
                if (remind.owner != remind.reporter):
                    msg = "%s : %s m'a dit de te rappeler "%(remind.owner, remind.reporter)
                    msg += date.decode("utf-8") + " que : %s"%(remind.description)
                else:
                    msg = "%s : comme convenu je te rappelle "%(remind.owner) 
                    msg += date.decode("utf-8") + " que : %s"%(remind.description)
                self.bot.say(msg)
            elif remind.date < self.lastcheck:
                self.bot.session.delete(remind)
                self.bot.session.commit()
        self.lastcheck = now
        time.sleep(10)
