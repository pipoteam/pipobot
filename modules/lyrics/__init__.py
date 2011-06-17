#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import lyricstime

class CmdLyrics:
    def __init__(self, bot):
        self.bot = bot
        self.command = "lyrics"
        self.desc = "Retourne des paroles."
        self.pm_allowed = True
            
    def answer(self, sender, message):
        print message

        res = lyricstime.query(message)
        return res

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdLyrics(None)
    print o.answer('pipo', '')
else:
    from .. import register
    register(__name__, CmdLyrics)

