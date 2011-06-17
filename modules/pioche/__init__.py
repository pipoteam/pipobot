#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random

class CmdPioche:
    def __init__(self, bot):
        self.bot = bot
        self.command = "pioche"
        self.desc = "pioche\nPioche une carte au hasard dans un jeu de 52 cartes"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        n = random.randint(0, 51)
        couleurs = ["pique", "coeur", "carreau", "trèfle"]
        noms = ["As"]+[str(i) for i in range(2, 11)]+ ["Valet", "Dame", "Roi"]
        return noms[n%13]+" de "+couleurs[n/13]


if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdPioche(None)
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdPioche)

