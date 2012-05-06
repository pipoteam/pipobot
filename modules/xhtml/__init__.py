#! /usr/bin/env python
#-*- coding: utf-8 -*-

import re
import pipobot.lib.utils
from pipobot.lib.modules import SyncModule, defaultcmd

class CmdXhtml(SyncModule):
    def __init__(self, bot):
        desc = "xhtml code_xhtml\nAfficher le code xhtml formaté"
        SyncModule.__init__(self, 
                            bot,  
                            desc = desc,
                            pm_allowed = False,
                            command = "xhtml",
                            )
    @defaultcmd
    def answer(self, sender, message):
        d = {}
        d["text"] = message
        d["xhtml"] = pipobot.lib.utils.xhtml2text(message)
        return d
