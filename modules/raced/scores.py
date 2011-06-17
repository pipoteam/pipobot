#! /usr/bin/python
# -*- coding: utf-8 -*-

import time
import sqlite3
from . import DB

class CmdRacedScores:
    def __init__(self, bot):
        self.bot = bot
        self.command = 'racedscores'
        self.desc = 'racedscores\nAffiche le palmarès actuel des raced'
        self.pm_allowed = True

    def answer(self, sender, message):
        """Affiche les scores des raced"""
        conn = sqlite3.connect(DB)
        conn.isolation_level = None
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM racedscores")
        except:
            c.execute("CREATE TABLE racedscores (jid_from TEXT, jid_to TEXT, score INT, submission INT)")
        c.execute("SELECT jid_from, jid_to, score, submission FROM racedscores ORDER BY score DESC")
        classement = c.fetchall()
        conn.close()

        if len(classement) != 0:
            sc = "\nRaced - scores :"
            pseudo = ""
            for row in classement:
                pseudo_from = self.bot.jid2pseudo(row[0])
                pseudo_to = self.bot.jid2pseudo(row[1])
                sc += "\n%-10s a battu %-8s fois %-10s" % (pseudo_from, row[2],
                                                           pseudo_to)
                sc += "                                           "
                sc += time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(row[3])))
            return sc
        else:
            return "Aucun race, bande de nuls !"
