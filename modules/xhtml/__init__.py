#! /usr/bin/env python
#-*- coding: utf-8 -*-

import re
import modules.utils
import lib.modules.SyncModule 

class CmdXhtml(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = "xhtml code_xhtml\nAfficher le code xhtml formaté"
        lib.modules.SyncModule.__init__(bot, 
                        desc = desc,
                        pm_allowed = False,
                        command = "xhtml",
                        )
            
    def answer(self, sender, message):
        d = {}
        d["text"] = message
        d["xhtml"] = modules.utils.xhtml2text(message)
        return d
