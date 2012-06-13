#! /usr/bin/python
# -*- coding: utf-8 -*-

from abstractblague import AbstractBlague
from pipobot.lib.modules import SyncModule
from model import Blagueur
import time, operator

class CmdBlague(AbstractBlague):
    """ Ajoute un point-blague à un collègue blagueur compétent """
    def __init__(self, bot):
        desc = u"Donnez un point blague à un ami ! écrivez !blague pseudo (10 s minimum d'intervalle)"
        AbstractBlague.__init__(self,
                                bot,
                                desc = desc,
                                command = "blague",
                                autocongratulation = "Un peu de modestie, merde",
                                premier = u"Félicitations %s, c'est ta première blague !",
                                operation = operator.add)

    def cmd_score(self, sender, message):
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
