#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import re

class CmdBoo:
    def __init__(self, bot):
        self.bot = bot
        self.command = "boo"
        self.desc = "!boo [quelqu'un] : Pour huer quelqu'un..."
        self.pm_allowed = True
            
    def answer(self, sender, message):
        toalmostall = []
        for people in self.bot.jids.iterkeys():
            if self.bot.jid2pseudo(people) != sender:
                if self.bot.jid2pseudo(people) != self.bot.name:
                    toalmostall.append(self.bot.jid2pseudo(people))
        if message == '':
            return "%s: %s vous dit BOOOOOOOUUUUHHH à tous !!! " % (" ".join(toalmostall), sender)
        elif message.lower() == self.bot.name.lower():
            return "%s: Personne ne me hue moi, PERSONNE !!!"%(sender)
        elif message.lower() == sender.lower():
            if sender.lower() == 'charlotte':
                return "%s: On le sait que t'es mauvaise... Mais c'est toujours bon à dire : BOOOOUUUUUUHHHH !!!" % (sender)
            else:
                return "%s: On le sait que t'es mauvais... Mais c'est toujours bon à dire : BOOOOUUUUUUHHHH !!!" % (sender)
        elif re.search("(^|\W)+charlotte($|\W)+", message.lower()): 
            return "Allez, tout le monde hue Charlotte !!! BOOOOUUUUUHHH !!! Sortez-la !!!"
        elif ' et ' in message.lower():
            return "Allez, tout le monde hue %s !!! BOOOOOUUUUHHH !!! Sortez-les !!!" % (message)
        else:
            return "Allez, tout le monde hue %s !!! BOOOOUUUUHHHH !!! Sortez-le !!!" % (message)

class FakeBot:
    def __init__(self):
        self.name = "Pipo-test"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    bot = FakeBot()
    o = CmdBoo(bot)
    print o.answer('xouillet', 'Bad Company')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdBoo)

