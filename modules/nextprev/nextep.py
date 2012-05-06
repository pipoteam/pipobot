#! /usr/bin/env python
#-*- coding: utf-8 -*-
from pipobot.lib.modules import SyncModule, defaultcmd
import core

class CmdNext(SyncModule):
    def __init__(self, bot):
        desc = "next [show1;show2;show3]\nAffiche les infos sur le prochain épisode en date de show1,show2,show3"
        SyncModule.__init__(self, 
                                bot,  
                                desc = desc,
                                command = "next")

    @defaultcmd
    def answer(self, sender, message):
        res = core.getdata(message, True)
        return res
