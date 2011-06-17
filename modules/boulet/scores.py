#! /usr/bin/python
# -*- coding: utf-8 -*-

import time
import sqlite3
from consts import DB

class CmdScoresBoulet:
    def __init__(self, bot):
        self.bot = bot
        self.command = 'scoresboulet'
        self.desc = 'scoresboulet\nAffiche le palmarès actuel des boulets'
        self.pm_allowed = True

    def answer(self, sender, message):
        """Affiche les scores des blagueurs"""
        conn = sqlite3.connect(DB)
        conn.isolation_level = None
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM scores")
        except:
            c.execute("CREATE TABLE scores (pseudo TEXT, score INT, submission INT)")

        c.execute("SELECT pseudo, score, submission FROM scores ORDER BY score DESC")
        classement = c.fetchall()
        conn.close()

        if len(classement) != 0:
            sc = "\nBoulets - scores :"
            pseudo = ""
            for row in classement:
                pseudo = self.bot.jid2pseudo(row[0])
                sc += "\n%-8s  -       %-10s" % (row[1], pseudo)
                sc += "                                           "
                sc += time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(row[2])))
            return sc
        else:
            return "Aucun boulet ? ben voyons... !"
