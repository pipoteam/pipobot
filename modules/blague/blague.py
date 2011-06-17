#! /usr/bin/python
# -*- coding: utf-8 -*-

import time
import sqlite3
from consts import DB

class CmdBlague:
    """ Ajoute un point-blague à un collègue blagueur compétent """
    def __init__(self, bot):
        self.command = "blague"
        self.bot = bot
        self.desc = "blague [pseudo]\nAjoute un point blague à [pseudo]"
        self.pm_allowed = False

    def answer(self, sender, message):
        send = ''
        if message == '':
            return u"Donnez un point blague à un ami ! écrivez !blague pseudo (10 s minimum d'intervalle)"
        sjid = self.bot.pseudo2jid(sender.strip())
        try:
            jid = self.bot.pseudo2jid(message)
        except KeyError:
            jid = "Sid"
           # return u"%s n'est pas là..." % message

        if sjid == jid:
            return "Un peu de modestie, merde"

        temps = int(time.time())
        # Connection db
        conn = sqlite3.connect(DB)
        conn.isolation_level = None
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM scores")
        except:
            c.execute("CREATE TABLE scores (pseudo TEXT, score INT, submission INT)")

        c.execute("SELECT score,submission FROM scores WHERE pseudo=?",(jid,))
        res = c.fetchall()
        if len(res) == 0:
            send = u"Félicitations %s, c'est ta première blague !" % message
            c.execute("INSERT INTO scores VALUES (?, 1, ?)", (jid, str(temps)))
        elif len(res) == 1:
            nouv_score = res[0]
            sc = int(nouv_score[0]) + 1
            ecart = temps - int(nouv_score[1])
            if ecart>10:
                c.execute("UPDATE scores SET score=?, submission=? WHERE pseudo=?",(str(sc), str(temps), jid))
                date_bl = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(nouv_score[1])))
                send = u"Nouveau score - %s : %d\n%d secondes depuis ta dernière blague (%s)" % (message, sc, ecart, date_bl)
        else:
            send = "Erreur, voir Bok :)"
        conn.commit()
        conn.close()
        return send
