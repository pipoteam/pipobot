#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
from pendu import Pendu

class CmdPendu:
    def __init__(self, bot):
        self.bot = bot
        self.command = "pendu"
        self.desc = """Un superbe jeu de pendu
pendu init : lance une partie avec un mot aléatoire (to be coded...)
pendu init [word] : lance une partie avec 'word' comme mot à trouver
pendu try [letter] : propose la lettre 'letter'
pendu played : affiche la liste des lettres déjà jouées"""
        self.pm_allowed = True
            
    def answer(self, sender, message):
        if not hasattr(self.bot, "pendu"): 
            self.bot.pendu = Pendu("")

        args = message.split()
        cmd = args[0].strip()
        try:
            argument = args[1].strip()
        except IndexError:
            argument = ""
        if cmd == "init":
            if argument == "":
                self.bot.pendu.word = "pipo" #TODO faire un random dans un dico
            else:
                self.bot.pendu.word = argument
                self.bot.say("Et c'est parti pour un pendu !")
        elif cmd == "try":
            if argument == "" or len(argument) > 1:
                return "Il faut proposer une lettre :s"
            else:
                return self.bot.pendu.propose(argument)

        elif cmd == "played":
            return self.bot.pendu.playedtostr()

class Fakebot:
    def __init__(self):
        self.name = "pipo"

if __name__ == '__main__':
    bot = Fakebot()
    p = CmdPendu(bot)
    while True:
        cmd = raw_input()
        print p.answer("seb", cmd)
else:
    from .. import register
    register(__name__, CmdPendu)

