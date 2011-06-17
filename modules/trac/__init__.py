#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3

#DB="/usr/local/share/botnet7-ng/modules/trac/trac.db"
DB = "/srv/http/trac.sleduc.fr/db/trac.db"

class CmdTrac:
    def __init__(self, bot):
        self.command = "trac"
        self.bot = bot
        self.desc = "trac [num]\nListe les tickets trac actifs ou en affiche un en détail"
	self.pm_allowed = True

    def answer(self, sender, message):
        send = "\n"
        # Connection db
        conn = sqlite3.connect(DB)
        conn.isolation_level = None
        c = conn.cursor()
        if message == '':
            c.execute("SELECT id, priority, summary FROM ticket WHERE status!='closed' ORDER BY priority")
            for id, p, summary in c.fetchall():
                send += "[%d] %s\n" % (id, summary)
            if send == "\n":
                send = "Pas de ticket ! Vous avez plus qu'à espérer ne pas vous faire contrôler"
                
        else:
            try:
                i = int(message)
            except:
                return "Merci de rentrer un numéro de ticket"
            c.execute("SELECT id, priority, summary, description FROM ticket WHERE id=? ORDER BY priority",(i,))
            id, p, summ, desc = c.fetchone()
            send += "[%d] %s\n%s\n" % (id, summ, desc)
        conn.commit()
        conn.close()
        return send

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdTrac(None)
    print o.answer('xouillet', '') 
    print o.answer('xouillet', '47')    
else:
    from .. import register
    register(__name__, CmdTrac)

