#! /usr/bin/python
# -*- coding: utf-8 -*-

from pipobot.lib.modules import SyncModule, defaultcmd

class CmdScores(SyncModule):
    """ Consulte les scores de certains modules """
    def __init__(self, bot):
        desc = "score [module] [params]\nConsulte les scores pour le module [module]"
        SyncModule.__init__(self, 
                        bot, 
                        desc = desc,
                        command = "score",
                        )
        self.avail_mods = {}

    def init_mods(self):
        if self.avail_mods == {}:
            for module in self.bot.modules:
                if hasattr(module, "cmd_score"):
                    self.avail_mods[module.command] = module.cmd_score
            self.desc += "\nModules disponibles : %s" % (", ".join(self.avail_mods.keys()))

    @defaultcmd
    def answer(self, sender, message):
        #Can't be done in init : we have to be sure that all modules have been loaded…
        self.init_mods()
        args = message.split()
        if args == []:
            return self.desc
        if args[0] in self.avail_mods:
            return self.avail_mods[args[0]](sender, args[1:])
        else:
            return self.desc
