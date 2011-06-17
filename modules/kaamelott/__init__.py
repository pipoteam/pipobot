#! /usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import random

class ListConfigParser(ConfigParser.RawConfigParser):   
    def get(self, section, option):
        "Redéfinition du get pour gérer les listes"
        value = ConfigParser.RawConfigParser.get(self, section, option)
        if (value[0] == "[") and (value[-1] == "]"):
            return eval(value)
        else:
            return value

class Kaamelott:
    def __init__(self, bot):
        self.bot = bot
        self.command = "kaamelott"
        self.desc = "Quelques citations de certaines personnes de kaamelott : arthur, burgonde, guethenoc, kadoc, karadoc, lancelot, leodagan, merlin, perceval."
        self.pm_allowed = True
        self.isMulticmd = True

        self.dico = {}
        config = ListConfigParser()
        config.read('modules/kaamelott/bidon.cfg')
        self.genericCmd = config.sections()
        for c in self.genericCmd:
            self.dico[c] = {}
            self.dico[c]['desc'] = config.get(c, 'desc')
            self.dico[c]['citation'] = config.get(c, 'citation') if type(config.get(c, 'citation')) == list else [config.get(c, 'citation')]
            

    def answer(self, sender, message):
        cmd = message.split(" ")[0][1:]
        message = message[1+len(cmd):].strip()
        if cmd == '':
            return "Il faut mettre une personne parmi la liste que tu peux aller voir tout seul dans le help !"
        elif message == '':
            return random.choice(self.dico[cmd]["citation"])
        else:
            return "Pourquoi un argument ?"


if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = Kaamelott(None)
    print o.answer('xouillet', 'argument')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, Kaamelott)

