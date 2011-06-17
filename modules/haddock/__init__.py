#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random

class Haddock:
    def __init__(self, bot):
        self.bot = bot
        self.command = "haddock"
        self.desc = "Les insultes du capitaine haddock :p."
        self.pm_allowed = True
        self.quotes = []
        path = "modules/haddock/bdd.txt"
        with open(path, 'r') as fichier:
            content = fichier.read()
            tmp = content.split(",")
            self.quotes = [elt.replace("&#8217;", "'") for elt in tmp]

    def answer(self, sender, message):
        tmp = ""
        if message == self.bot.name:
            tmp = "%s: c'est toi qui est un"%(sender)
        elif message != '':
            tmp = "%s: "%(message)
        tmp += random.choice(self.quotes)
        return tmp

class FakeBot:
    def __init__(self):
        self.name = "pipo"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = Haddock(FakeBot())
    print o.answer('xouillet', 'pipo')    
else:
    from .. import register
    register(__name__, Haddock)

