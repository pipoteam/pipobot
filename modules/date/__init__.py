#! /usr/bin/env python
#-*- coding: utf-8 -*-

import time

class CmdDate:
    def __init__(self, bot):
        self.bot = bot
        self.command = "date"
        self.desc = "date : Affiche la date et l'heure actuelle"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        return time.strftime("Nous sommes le %d/%m/%Y et il est %H:%M")

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdDate(None)
    print o.answer('xouillet', ' argument')    
else:
    from .. import register
    register(__name__, CmdDate)


