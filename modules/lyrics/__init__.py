#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import lyricstime
from lib.modules import SyncModule, answercmd

class CmdLyrics(SyncModule):
    def __init__(self, bot):
        desc = "Retourne des paroles."
        SyncModule.__init__(self, 
                            bot,  
                            desc = desc,
                            command = "lyrics")
            
    @answercmd
    def answer(self, sender, message):
        res = lyricstime.query(message)
        return res
