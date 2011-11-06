#! /usr/bin/env python
#-*- coding: utf-8 -*-
import lib.modules.SyncModule
import core

class CmdNext(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = "next [show1;show2;show3]\nAffiche les infos sur le prochain épisode en date de show1,show2,show3"
        lib.modules.SyncModule.__init__(bot, 
                                desc = desc,
                                command = "next")

    @answercmd() 
    def answer(self, sender, message):
        res = core.getdata(message, True)
        return res
