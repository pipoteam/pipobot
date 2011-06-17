#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import xmpp
import ConfigParser


class CmdSay:
    def __init__(self, bot):
        self.bot = bot
        self.command = "say"
        self.desc = "say [someone] [something]\nVa dire quelque chose à quelqu'un en privé^^'"
        self.pm_allowed = False
        self.dico = {}
        config = ConfigParser.RawConfigParser()
        config.read('modules/say/lst.cfg')
        self.genericCmd = config.sections()
        for people in config.options("adresses"):
            adresse = config.get("adresses", people)
            self.dico[people] = adresse


    def getUsers(self):
        res = "Liste des utilisateurs disponibles :\n"
        for user,jid in self.dico.iteritems():
            res += "\t%s - %s\n"%(user, jid)
        return res[:-1]

    def answer(self, sender, message):
        tojid,text = message.split(' ', 1)
        text = "C'est quelqu'un qui m'a dit...de te dire que...%s"%(text)
        if tojid in self.dico.keys():
            self.bot.send(xmpp.protocol.Message(self.dico[tojid], text))
            return "Je crois que le message est passé..."
        else:
            res = "Il n'y a pas d'abonnés au numéro que vous avez demandé\n"
            res += self.getUsers()
            return res

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdSay(None)
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdSay)

