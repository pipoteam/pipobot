#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random

class Balise:
    def __init__(self, bot):
        self.bot = bot
        self.command = "b"
        self.desc = "!b auteur contenu : <auteur> contenu </auteur> "
        self.pm_allowed = True

    def answer(self, sender, message):
        try:
            args = message.split(" ",1)
            balise = args[0]
            message = args[1]
            res = "<%s> %s </%s>"%(balise, message, balise)
        except IndexError:
            return "Tu ferais mieux de lire le man : %s"%(self.desc)
        return res

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = Balise(None)
    print o.answer('xouillet', '!b Altibelli C\'est trivial !')    
else:
    from .. import register
    register(__name__, Balise)

