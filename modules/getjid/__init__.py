#! /usr/bin/env python
#-*- coding: utf-8 -*-

class CmdGetjid:
    def __init__(self, bot):
        self.bot = bot
        self.command = "getjid"
        self.desc = "getjid [nom]\nAffiche la première partie du jid pour découvrir qui se cache derrière un pseudo"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        if self.bot.jids == {}:
            return "Jppt car j'ai pas les droits"
        try:
            if message == '':
                return self.bot.pseudo2jid(sender)
            else:
                return self.bot.pseudo2jid(message)
        except KeyError:
            return "%s: mais t'es con ou quoi ? Tu ne vois pas que %s n'est pas là ?!"%(sender, message)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, CmdGetjid)

