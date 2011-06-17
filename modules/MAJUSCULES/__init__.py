#! /usr/bin/env python
#-*- coding: utf-8 -*-
import re

class CmdMajuscules:
    def __init__(self, bot):
        self.bot = bot
            
    def answer(self, sender, message):
        if type(message) not in (str, unicode):
            return
        cars = len(message.replace(" ",""))
        majs = len(re.findall("[A-Z]", message))
        ratio = float(majs) / cars
        if ratio > 0.5 and cars > 10:
            return "%s : ON GUEULE PAS ICI !!!"%(sender)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, CmdMajuscules)

