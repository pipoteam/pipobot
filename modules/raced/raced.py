#! /usr/bin/python
# -*- coding: utf-8 -*-

import time
import sqlite3
from . import DB

class CmdRaced:
    """ Ajoute un point-raced à un collègue lent"""
    def __init__(self, bot):
        self.command = "raced"
        self.bot = bot
        self.desc = "raced pseudo\nAjoute un point raced à /me envers pseudo"
	self.pm_allowed = False

    def answer(self, sender, message):
        send = ''
        if message == '':
            return u"Donnez vous un point raced envers un ami ! écrivez !raced pseudo (10 s minimum d'intervalle)"
        sjid = self.bot.pseudo2jid(sender.strip())
        try:
            jid = self.bot.pseudo2jid(message)
        except KeyError:
            return u"%s n'est pas là..." % message

        if sjid == jid:
            return "Sans vouloir contrarier, ça va être dur là…"

        temps = int(time.time())
        # Connection db
        conn = sqlite3.connect(DB)
        conn.isolation_level = None
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM racedscores")
        except:
            c.execute("CREATE TABLE racedscores (jid_from TEXT, jid_to TEXT, score INT, submission INT)")

        c.execute("SELECT score,submission FROM racedscores WHERE jid_from=? AND jid_to=?",(sjid, jid))
        res = c.fetchall()
        if len(res) == 0:
            send = u"Félicitations %s, c'est la première fois que tu bats %s!" % (sender.strip(), message)
            c.execute("INSERT INTO racedscores VALUES (?, ?, 1, ?)", (sjid, jid, str(temps)))
        elif len(res) == 1:
            nouv_score = res[0]
            sc = int(nouv_score[0]) + 1
            ecart = temps - int(nouv_score[1])
            if ecart>10:
                c.execute("UPDATE racedscores SET score=?, submission=? WHERE jid_from=? AND jid_to=?",(str(sc), str(temps), sjid, jid))
                date_bl = time.strftime("le %d/%m/%Y a %H:%M", time.localtime(float(nouv_score[1])))
                send = u"Nouveau score - %s : %d\n%d secondes depuis la dernière fois que tu as battu %s (%s)" % (sender.strip(), sc, ecart, message, date_bl)
        else:
            send = "Erreur, voir Bok :)"
        conn.commit()
        conn.close()
        return send
