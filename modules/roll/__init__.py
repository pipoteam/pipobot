#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random

class CmdRoll:
    def __init__(self, bot):
        self.bot = bot
        self.command = "roll"
        self.desc = """Le jugement des dieux !... Enfin de Pipo !
roll [entier] : renvoie un entier entre 1 et [entier]
roll [x,y,z] : renvoie un choix aléatoire entre x, y et z"""
        self.pm_allowed = True
            
    def answer(self, sender, message):
        if message.isdigit() and int(message) > 0:
            n = random.randint(1, int(message))
            return "%d !"%(n)
        elif message.strip() != "":
            return "%s !"%random.choice(message.split(","))
        else:
            return "Utilise un entier !"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, CmdRoll)

