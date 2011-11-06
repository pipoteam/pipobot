#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import time
import lib.modules.SyncModule

class Ola(lib.modueles.SyncModule):
    def __init__(self, bot):
        desc = "Fait la ola."
        lib.modules.SyncModule.__init__(bot,
                                desc = desc,
                                command = "ola")

    @answercmd()
    def answer(self, sender, message):
        if message == "":
            message = str(random.randint(0, 1))
        if not message.isdigit():
            return "On veut un entier quand même..."
        res = ["\o/ .o. .o. .o.",".o. \o/ .o. .o.",".o. .o. \o/ .o.",".o. .o. .o. \o/"]
        if int(message) % 2 != 0:
            res.reverse()
        return res
