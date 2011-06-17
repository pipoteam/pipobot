#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import threading, traceback
import time
import lib.consts
from lib.bddremind import BddReminder

class AsyncReminder(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.alive = True
        self.command = 'reminder'
        self.reminder = BddReminder(lib.consts.DB)
        self.bot = bot

    def run(self):
        lastcheck = time.time()
        while self.alive:
            self.reminder = BddReminder(lib.consts.DB)
            now = time.time()
            reminds = self.reminder.lstreminds()
            for remind in reminds:
                if remind[-2] >= lastcheck and remind[-2] < now:
                    date = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(remind[3])))
                    if (remind[1] != remind[4]):
                        msg = "%s : %s m'a dit de te rappeler "%(remind[1], remind[4])
                        msg += date.decode("utf-8") + " que : %s"%(remind[2])
                    else:
                        msg = "%s : comme convenu je te rappelle "%(remind[1]) 
                        msg += date.decode("utf-8") + " que : %s"%(remind[2])
                    self.bot.say(msg)
                elif remind[-2] < lastcheck:
                    self.reminder.delreminder(remind[0])
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
