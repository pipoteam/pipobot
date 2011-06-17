#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sqlite3

DB = "/srv/http/trac.sleduc.fr/db/trac.db"
repo = "/srv/hg/repos/botjabber/"

class CmdHg:
    def __init__(self, bot):
        self.command = "hg"
        self.bot = bot
        self.desc = "hg [num]\nMontre le dernier changeset ou affiche les détails d'un changeset donné"
	self.pm_allowed = True

    def answer(self, sender, message):
        import popen2
        send = ""
        try:
            if message == "":
                cmd = "hg tip -R %s"%(repo)
                r, w, e = popen2.popen3(cmd)
                send = r.read()
                r.close()
                e.close()
                w.close()
            else:
                cmd = "hg log -R %s -r %s"%(repo, message)
                r, w, e = popen2.popen3(cmd)
                send = r.read()
                r.close()
                e.close()
                w.close()
        except:
            send = "Erreur !"
        if send == "":
            send = "Pas de réponse, surement un mauvais argument (révision inexistante)"
        return send

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdHg(None)
    print o.answer('xouillet', '') 
    print o.answer('xouillet', '47')    
else:
    from .. import register
    register(__name__, CmdHg)

