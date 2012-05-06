#! /usr/bin/python
# -*- coding: utf-8 -*-

from model import Blagueur
from pipobot.lib.modules import SyncModule, defaultcmd
import time

class CmdBlague(SyncModule):
    """ Ajoute un point-blague à un collègue blagueur compétent """
    def __init__(self, bot):
        desc = "blague [pseudo]\nAjoute un point blague à [pseudo]"
        SyncModule.__init__(self, 
                        bot, 
                        desc = desc,
                        pm_allowed = False,
                        command = "blague",
                        )

    @defaultcmd
    def answer(self, sender, message):
        send = ''
        if message == '':
            return u"Donnez un point blague à un ami ! écrivez !blague pseudo (10 s minimum d'intervalle)"
        sjid = self.bot.occupants.pseudo_to_jid(sender.strip())
        jid = self.bot.occupants.pseudo_to_jid(message)
        if jid == "":
            return "%s n'est pas dans le salon !" % message

        if sjid == jid:
            return "Un peu de modestie, merde"

        temps = int(time.time())

        res = self.bot.session.query(Blagueur).filter_by(pseudo=jid).all()
        if len(res) == 0:
            b = Blagueur(jid, 1, temps)
            self.bot.session.add(b)
            send = u"Félicitations %s, c'est ta première blague !" % message
        else:
            min_delay = 10
            blag = res[0]
            ecart = temps - blag.submission
            if ecart > min_delay:
                date_bl = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(blag.submission)))
                send =  u"Nouveau score - %s : %d\n%d secondes depuis ta dernière blague (%s)" % (message, blag.score + 1, ecart, date_bl)
                blag.score += 1
                blag.submission = temps
            else:
                send = "Ta dernière blague date de plus de %s secondes !"%(min_delay)
        self.bot.session.commit()
        return send

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
