#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import time

class Ola:
    def __init__(self, bot):
        self.bot = bot
        self.command = "ola"
        self.desc = "Fait la ola."
        self.pm_allowed = True

    def answer(self, sender, message):
        if message == "":
            message = str(random.randint(0, 1))
        if not message.isdigit():
            return "On veut un entier quand même..."
        res = ["\o/ .o. .o. .o.",".o. \o/ .o. .o.",".o. .o. \o/ .o.",".o. .o. .o. \o/"]
        if int(message) % 2 != 0:
            res.reverse()
        return res

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = Ola(None)
    print o.answer('xouillet', '2')
else:
    from .. import register
    register(__name__,Ola)

