#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from model import Racer
from sqlalchemy.sql.expression import desc
from sqlalchemy import func
from lib.modules import SyncModule, defaultcmd

class CmdRacedScores(SyncModule):
    def __init__(self, bot):
        desc = 'racedscores\nAffiche le palmarès actuel des raced'
        SyncModule.__init__(self, 
                            bot, 
                            desc = desc,
                            command = "racedres",
                            )
    @defaultcmd
    def answer(self, sender, message):
        """Affiche les scores des raced"""
        classement = self.bot.session.query(Racer).order_by(desc(Racer.score), Racer.jid_from).all()

        if len(classement) != 0:
            sc = "\nRaced - scores :\n"
            sc += " " + 82*"_"
            for racer in classement:
                sc += "\n| "
                pseudo_from = self.bot.occupants.jid_to_pseudo(racer.jid_from)
                pseudo_to = self.bot.occupants.jid_to_pseudo(racer.jid_to)

                if len(pseudo_from) > 30:
                    sc += "%s " % (pseudo_from[:30])
                else:
                    sc += "%-30s " % (pseudo_from)
                sc += "a battu %-3s fois " % (racer.score)

                if len(pseudo_to) > 30:
                    sc += "%s " % (pseudo_to[:30])
                else:
                    sc += "%-30s " % (pseudo_to)
                sc += " |"
            sc += "\n"
            sc +=  "|" + 81*"_" + "|"
            return {"text" : sc, "monospace" : True}
        else:
            return "Aucun race, bande de nuls !"
