#! /usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import random
import re

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

class CmdAlacon:
    def __init__(self, bot):
        self.bot = bot
        self.command = "cmdalacon"
        self.pm_allowed = True
        self.isMulticmd = True
        self.dico = {}
        self.readconf()
    
    def readconf(self):
        config = ConfigParser.RawConfigParser()
        config = ListConfigParser()
        config.read('modules/cmdalacon/cmdlist.cfg')
        self.genericCmd = config.sections()
        for c in self.genericCmd:
            self.dico[c] = {}
            self.dico[c]['desc'] = config.get(c, 'desc') 
            self.dico[c]['toNobody'] = config.get(c, 'toNobody') if type(config.get(c, 'toNobody')) == list else [config.get(c, 'toNobody')]
            try:
                self.dico[c]['toSender'] = config.get(c, 'toSender') if type(config.get(c, 'toSender')) == list else [config.get(c, 'toSender')]
            except:
                self.dico[c]['toSender'] = self.dico[c]['toNobody']
            try:
                self.dico[c]['toBot'] = config.get(c, 'toBot') if type(config.get(c, 'toBot')) == list else [config.get(c, 'toBot')]
            except:
                try:
                    self.dico[c]['toBot'] = self.dico[c]['toSender']
                except:
                    self.dico[c]['toBot'] = self.dico[c]['toNobody']
            try:
                self.dico[c]['toSomebody'] = config.get(c, 'toSomebody') if type(config.get(c, 'toSomebody')) == list else [config.get(c, 'toSomebody')]
            except:
                self.dico[c]['toSomebody'] = self.dico[c]['toNobody']
            

    def getDesc(self, cmd):
        if cmd in self.genericCmd:
            return "%s [nom] : %s" % (cmd, self.dico[cmd]['desc'])

    def answer(self, sender, message):
        cmd = message.split(" ")[0][1:]
        message = message[1+len(cmd):].strip()
        if self.bot.pseudo2role(self.bot.name) == "moderator":
            toall = [self.bot.jid2pseudo(people) for people in self.bot.jids.iterkeys() if self.bot.pseudo2jid(people) not in [self.bot.pseudo2jid(sender), self.bot.pseudo2jid(self.bot.name)]]
        else:
            toall = [self.bot.jid2pseudo(people) for people in self.bot.droits.iterkeys() if self.bot.jid2pseudo(people) not in [self.bot.name, sender]]
        replacement = {"__somebody__":message, "__sender__":sender, "_all_":" ".join(toall)}
        if message.lower() == sender.lower():
            key = "toSender"
        elif message == '':
            key = "toNobody"
        elif message.lower() == self.bot.name.lower():
            key = "toBot"
        else:
            key = "toSomebody"
        return multiwordReplace(multiwordReplace(random.choice(self.dico[cmd][key]), replacement), replacement)


if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdAlacon(None)
    print o.answer('xouillet', 'argument')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdAlacon)

