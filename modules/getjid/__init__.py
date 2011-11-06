#! /usr/bin/env python
#-*- coding: utf-8 -*-

from lib.modules import SyncModule, answercmd

class CmdGetjid(SyncModule):
    def __init__(self, bot):
        desc = "getjid [nom]\nAffiche la première partie du jid pour découvrir qui se cache derrière un pseudo"
        SyncModule.__init__(bot, 
                                    desc = desc,
                                    command = "getjid")
            
    @answercmd
    def answer(self, sender, message):
        if self.bot.jids == {}:
            return "Jppt car j'ai pas les droits"
        try:
            if message == '':
                return self.bot.pseudo2jid(sender)
            else:
                return self.bot.pseudo2jid(message)
        except KeyError:
            return "%s: mais t'es con ou quoi ? Tu ne vois pas que %s n'est pas là ?!"%(sender, message)
