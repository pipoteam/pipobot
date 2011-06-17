#! /usr/bin/env python
#-*- coding: utf-8 -*-
import core

class CmdNextep:
    def __init__(self, bot):
        self.bot = bot
        self.command = "next"
        self.desc = "next [show1;show2;show3]\nAffiche les infos sur le prochain épisode en date de show1,show2,show3"
        self.pm_allowed = True

            
    def answer(self, sender, message):
        res = core.getdata(message, True)
        return res

if __name__ == '__main__':
    #Placer ici les tests unitaires
    c = CmdNextep(None)
    print c.answer("john", "ncis; futurama")
    print c.answer("john", "himym")
    print c.answer("john", "futurama")
else:
    from .. import register
    register(__name__, CmdNextep)

