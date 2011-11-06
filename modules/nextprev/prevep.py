#! /usr/bin/env python
#-*- coding: utf-8 -*-
import lib.modules.SyncModule
import core

class CmdPrevep(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = """prev [show1;show2;show3]
Affiche les infos sur le dernier épisode en date de show1,show2,show3"""
        lib.modules.SyncModule.__init__(bot,
                                desc = desc,
                                command = "prev")

    @answercmd()            
    def answer(self, sender, message):
        res = core.getdata(message, False)
        return res
