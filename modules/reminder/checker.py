#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import threading, traceback
import time
from model import Remind

class AsyncReminder(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.alive = True
        self.command = 'reminder'
        self.bot = bot

    def run(self):
        lastcheck = time.time()
        while self.alive:
            reminds = self.bot.session.query(Remind).order_by(Remind.date).all()
            now = time.time()
            for remind in reminds:
                if remind.date >= lastcheck and remind.date < now:
                    date = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(remind.date)))
                    if (remind.owner != remind.reporter):
                        msg = "%s : %s m'a dit de te rappeler "%(remind.owner, remind.reporter)
                        msg += date.decode("utf-8") + " que : %s"%(remind.description)
                    else:
                        msg = "%s : comme convenu je te rappelle "%(remind.owner) 
                        msg += date.decode("utf-8") + " que : %s"%(remind.description)
                    self.bot.say(msg)
                elif remind.date < lastcheck:
                    self.bot.session.delete(remind)
                    self.bot.session.commit()
            lastcheck = now
            time.sleep(10)

    def stop(self):
        self.alive = False

class FakeBot:
    def __init__(self):
        self.name = "testeur"

    def say(self, msg):
        print msg

if __name__ == '__main__':
    #Placer ici les tests unitaires
    b = FakeBot()
    t = AsyncReminder(b)
    t.start()
