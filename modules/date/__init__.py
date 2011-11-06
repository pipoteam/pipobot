#! /usr/bin/env python
#-*- coding: utf-8 -*-

import time
from lib.modules import SyncModule, answercmd

class CmdDate(SyncModule):
    def __init__(self, bot):
        desc = "date : Affiche la date et l'heure actuelle"
        SyncModule.__init__(bot, 
                                    desc = desc,
                                    command = "date")

    @answercmd    
    def answer(self, sender, message):
        return time.strftime("Nous sommes le %d/%m/%Y et il est %H:%M")
