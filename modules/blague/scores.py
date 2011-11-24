#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from lib.modules import SyncModule, defaultcmd
from model import Blagueur

class CmdScores(SyncModule):
    def __init__(self, bot):
        desc = 'scores\nAffiche le palmarès actuel des blagueurs'
        SyncModule.__init__(self, 
                        bot,  
                        desc = desc,
                        command = "scores",
                        )

    @defaultcmd
    def answer(self, sender, message):
        """Affiche les scores des blagueurs"""
        classement = self.bot.session.query(Blagueur).order_by(Blagueur.score).all()
        if len(classement) != 0:
            classement.reverse()
            sc = "\nBlagounettes - scores :"
            pseudo = ""
            sc += "\n" + 75*"_"
            for blag in classement:
                pseudo = self.bot.occupants.jid_to_pseudo(blag.pseudo)
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
