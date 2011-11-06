#! /usr/bin/env python
#-*- coding: utf-8 -*-

import re
import lib.utils
from lib.modules import SyncModule, answercmd 

class CmdXhtml(SyncModule):
    def __init__(self, bot):
        desc = "xhtml code_xhtml\nAfficher le code xhtml formaté"
        SyncModule.__init__(self, 
                            bot,  
                            desc = desc,
                            pm_allowed = False,
                            command = "xhtml",
                            )
            
    def answer(self, sender, message):
        d = {}
        d["text"] = message
        d["xhtml"] = libs.utils.xhtml2text(message)
        return d
