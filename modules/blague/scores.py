#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from model import Blagueur

class CmdScores:
    def __init__(self, bot):
        self.bot = bot
        self.command = 'scores'
        self.desc = 'scores\nAffiche le palmarès actuel des blagueurs'
        self.pm_allowed = True

    def answer(self, sender, message):
        """Affiche les scores des blagueurs"""
        classement = self.bot.session.query(Blagueur).order_by(Blagueur.score).all()
        if len(classement) != 0:
            classement.reverse()
            sc = "\nBlagounettes - scores :"
            pseudo = ""
            sc += "\n" + 75*"_"
            for blag in classement:
                pseudo = self.bot.jid2pseudo(blag.pseudo)
                sc += "\n| %-4s  -  " % (blag.score)
                if len(pseudo) > 30:
                    sc += "%s " % (pseudo[:30])
                else:
                    sc += "%-30s " % (pseudo)
                sc += time.strftime(" dernière le %d/%m/%Y à %H:%M |", time.localtime(float(blag.submission)))
            sc += "\n|" + 73*"_" + "|"
            return {"text" : sc, "monospace" : True}
        else:
            return "Aucune blague, bande de nuls !"
