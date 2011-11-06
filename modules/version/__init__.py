#! /usr/bin/python
# -*- coding: utf-8 -*-
from mercurial import ui, hg
import time
import os
import lib.modules.SyncModule 

class CmdVersion(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = "version: donne la version (révision hg) du bot"
        lib.modules.SyncModule.__init__(bot, 
                        desc = desc,
                        command = "version",
                        )

    @answercmd
    def answer(self, sender, message):
        u = ui.ui()
        repo = hg.repository(u, os.getcwd())
        rev = len(repo) - 1
        stamp = repo[rev].date()[0]
        date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(stamp))
        res = "Je suis à la révision %s, datant du %s" % (rev, date)
        return res
