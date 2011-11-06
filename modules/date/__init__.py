#! /usr/bin/env python
#-*- coding: utf-8 -*-

import time
import lib.modules.SyncModule

class CmdDate(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = "date : Affiche la date et l'heure actuelle"
        lib.modules.SyncModule.__init__(bot, 
                                    desc = desc,
                                    command = "date")

    @answercmd()    
    def answer(self, sender, message):
        return time.strftime("Nous sommes le %d/%m/%Y et il est %H:%M")
