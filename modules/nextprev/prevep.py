#! /usr/bin/env python
#-*- coding: utf-8 -*-
from pipobot.lib.modules import SyncModule, defaultcmd
import core

class CmdPrev(SyncModule):
    def __init__(self, bot):
        desc = """prev [show1;show2;show3]
Affiche les infos sur le dernier épisode en date de show1,show2,show3"""
        SyncModule.__init__(self, 
                                bot, 
                                desc = desc,
                                command = "prev")

    @defaultcmd
    def answer(self, sender, message):
        res = core.getdata(message, False)
        return res
