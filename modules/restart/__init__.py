# -*- coding: utf-8 -*-
from pipobot.lib.modules import SyncModule, answercmd

class Restart(SyncModule):
    """ A module to reload the config for a bot and restart it """
    def __init__(self, bot):
        desc = "!restart : restart le bot"
        SyncModule.__init__(self, bot, desc, "restart")

    @answercmd("^$")
    def answer(self, sender, args):
        #TODO: handle authorizations
        self.bot.restart()
