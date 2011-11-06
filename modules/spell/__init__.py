#! /usr/bin/env python
#-*- coding: utf-8 -*-
import enchant
import lib.modules.SyncModule

class CmdSpell(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = """Correction orthographique
spell check : vérifie si un mot existe ou pas
spell suggest : donne les mots approchants"""
        lib.modules.SyncModule.__init__(bot, 
                                desc = desc,
                                command = "spell")
    
    @answercmd()
    def answer(self, sender, message):
        dico = enchant.Dict("fr_FR")
        args = message.split()
        mot = args[0]
        if len(args) < 1:
            return "RTFM : tu es à court d'arguments..."
        tmp = dico.check(mot)
        suggestions = dico.suggest(mot)
        if tmp:
            suggestions.remove(mot)
            return "Et oui, '%s' existe, tout comme %s"%(mot, ", ".join(suggestions))
        else:
            if suggestions == []:
                return "Ah bah là c'est tellement mauvais...ça ressemble à rien %s !!"%(mot)
            res = "Suggestions possibles pour %s : "%(mot)
            res += "; ".join(suggestions)
            return res
