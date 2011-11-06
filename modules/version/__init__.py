#! /usr/bin/python
# -*- coding: utf-8 -*-
from mercurial import ui, hg
import time
import os

class CmdVersion:
    def __init__(self, bot):
        self.command = "version"
        self.bot = bot
        self.desc = "version: donne la version (révision hg) du bot"
        self.pm_allowed = True

    def answer(self, sender, message):
        u = ui.ui()
        repo = hg.repository(u, os.getcwd())
        rev = len(repo) - 1
        stamp = repo[rev].date()[0]
        date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(stamp))
        res = "Je suis à la révision %s, datant du %s" % (rev, date)
        return res
                
if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdVersion(None)
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdVersion)

