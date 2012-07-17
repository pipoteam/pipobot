#! /usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import logging
import os
import random
import re
from pipobot.lib.modules import MultiSyncModule, defaultcmd

def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))
    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)


class ListConfigParser(ConfigParser.RawConfigParser):
    def get(self, section, option):
        "Redéfinition du get pour gérer les listes"
        value = ConfigParser.RawConfigParser.get(self, section, option)
        if (value[0] == "[") and (value[-1] == "]"):
            return eval(value)
        else:
            return value

class CmdAlacon(MultiSyncModule):
    def __init__(self, bot):
        commands = self.readconf(bot)
        MultiSyncModule.__init__(self,
                        bot,
                        commands=commands)

    def extract_to(self, config, cmd, value, backup):
        try:
            v = config.get(cmd, value)
        except ConfigParser.NoOptionError :
            v = config.get(cmd, backup)
        if type(v) != list:
            v = [v]
        self.dico[cmd][value] = v

    def readconf(self, bot):
        #name, description and actions associated to each command
        self.dico = {}
        #To initialize MultiSyncModule
        commands = {}

        settings = bot.settings
        config_path = ''
        try:
            config_path = settings['modules']['cmdalacon']['config_path']
        except KeyError:
            config_dir = bot.module_path["cmdalacon"]
            config_path = os.path.join(config_dir, "cmdlist.cfg")

        config = ListConfigParser()
        config.read(config_path)
        for c in config.sections() :
            self.dico[c] = {}
            self.dico[c]['desc'] = config.get(c, 'desc')
            commands[c] = self.dico[c]['desc']
            self.dico[c]['toNobody'] = config.get(c, 'toNobody') if type(config.get(c, 'toNobody')) == list else [config.get(c, 'toNobody')]
            self.extract_to(config, c, "toSender", "toNobody")
            self.extract_to(config, c, "toBot", "toNobody")
            self.extract_to(config, c, "toSomebody", "toNobody")
        return commands

    @defaultcmd
    def answer(self, cmd, sender, message):
        toall = self.bot.occupants.get_all(" ", [self.bot.name, sender])
        replacement = {"__somebody__" : message, "__sender__" : sender, "_all_" : toall}
        if message.lower() == sender.lower():
            key = "toSender"
        elif message == '':
            key = "toNobody"
        elif message.lower() == self.bot.name.lower():
            key = "toBot"
        else:
            key = "toSomebody"
        return multiwordReplace(multiwordReplace(random.choice(self.dico[cmd][key]), replacement), replacement)
