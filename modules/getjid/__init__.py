#! /usr/bin/env python
#-*- coding: utf-8 -*-
from lib.modules import SyncModule, defaultcmd

class CmdGetjid(SyncModule):
    def __init__(self, bot):
        desc = "getjid [nom]\nAffiche la première partie du jid pour découvrir qui se cache derrière un pseudo"
        SyncModule.__init__(self, 
                            bot, 
                            desc = desc,
                            command = "getjid",
                            )

    @defaultcmd 
    def answer(self, sender, message):
        if self.bot.jids == {}:
            return "Jppt car j'ai pas les droits"
        who = sender if message == "" else message
        jid = self.bot.pseudo2jid(who)
        if jid == "":
            return "%s n'est pas dans le salon" % who
        else:
            return jid
