#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
from pendu import Pendu
from lib.modules import SyncModule, answercmd

class CmdPendu(SyncModule):
    def __init__(self, bot):
        desc = """Un superbe jeu de pendu
pendu init : lance une partie avec un mot aléatoire (to be coded...)
pendu init [word] : lance une partie avec 'word' comme mot à trouver
pendu try [letter] : propose la lettre 'letter'
pendu played : affiche la liste des lettres déjà jouées"""
        SyncModule.__init__(self, 
                                bot, 
                                desc = desc,
                                command = "pendu")

    #TODO rewrite using decorators
    @answercmd 
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
                self.bot.say("Et c'est parti pour un pendu !")
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
