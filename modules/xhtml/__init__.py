#! /usr/bin/env python
#-*- coding: utf-8 -*-

import re
import lib.utils

class CmdXhtml:
    def __init__(self, bot):
        self.bot = bot
        self.command = "xhtml"
        self.desc = "xhtml code_xhtml\nAfficher le code xhtml formaté"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        return (lib.utils.xhtml2text(message), message)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdXhtml(None)
    print o.answer('xouillet', 'argument')
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdXhtml)

