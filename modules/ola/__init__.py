#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import time
from pipobot.lib.modules import SyncModule, defaultcmd

class Ola(SyncModule):
    def __init__(self, bot):
        desc = "Fait la ola."
        SyncModule.__init__(self, 
                                bot, 
                                desc = desc,
                                command = "ola")

    @defaultcmd
    def answer(self, sender, message):
        if message == "":
            message = str(random.randint(0, 1))
        if not message.isdigit():
            return "On veut un entier quand même..."
        res = ["\o/ .o. .o. .o.",".o. \o/ .o. .o.",".o. .o. \o/ .o.",".o. .o. .o. \o/"]
        if int(message) % 2 != 0:
            res.reverse()
        return res
