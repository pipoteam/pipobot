#! /usr/bin/env python
#-*- coding: utf-8 -*-
from pipobot.lib.modules import SyncModule, defaultcmd

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
        who = sender if message == "" else message
        jid = self.bot.occupants.pseudo_to_jid(who)
        if jid == "":
            return "%s n'est pas dans le salon ou je n'ai pas le droit de lire les jid…" % who
        else:
            return jid
