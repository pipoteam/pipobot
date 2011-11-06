#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import lyricstime
import lib.modules.SyncModule

class CmdLyrics(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = "Retourne des paroles."
        lib.modules.SyncModule.__init__(bot, 
                                    desc = desc,
                                    command = "lyrics")
            
    @answercmd()
    def answer(self, sender, message):
        res = lyricstime.query(message)
        return res
