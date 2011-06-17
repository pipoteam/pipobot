#! /usr/bin/env python
#-*- coding: utf-8 -*-
import xmpp
import random
from threading import Timer
import modules.utils

class CmdMute:
    def __init__(self, bot):
        self.bot = bot
        self.command = "mute"
        self.desc = "mute [nom]\n[nom] ne peut plus parler sur le salon !!!"
        self.pm_allowed = True

    def restore(self, name):
        modules.utils.unmute(name, self.bot)
            
    def answer(self, sender, message):
        role_sender = self.bot.pseudo2role(sender)
        reasonfail = ["%s: TPPT !!!",
                      "%s: Je n'obéis qu'au personnel compétent",
                      "%s: Tu crois vraiment que je vais t'obéir",
                      "%s: Non mais tu te crois où ? oO",
                      "%s: J'vais l'dire aux modérateurs"]
        reasonkick = ["TU TE TAIS %s",
                      "Désolé %s, je ne fais qu'obéir aux ordres"]

        lst = message.split(" ")
        rapport = ""
        if len(lst) == 2:
            if lst[0] == "undo":
                who = lst[1]
                modules.utils.unmute(who, self.bot)
                return "%s peut maintenant parler"%(who)

        for muted in lst:
            authorised = False
            orNot = False
            if muted == self.bot.name:
                rapport += "Je vais pas me virer moi-même oO\n"
                continue
            try:
                jidmuted = self.bot.pseudo2jid(muted)
                jidsender = self.bot.pseudo2jid(sender)
                if jidmuted == jidsender:
                    if muted == sender:
                        rapport += "Tu veux te muter toi-même ?\n"
                elif role_sender != "moderator":
                    orNot = True
                    authorised = True
                    toMute = sender
                    rapport += "%s n'a pas le droit de muter %s\n"%(sender, muted)
                else:
                    authorised = True
                    toMute = muted
                    rapport += "j'ai muté %s pour toi !\n"%(muted)
                    
            except:
                rapport += "%s n'est pas dans le salon\n"%(muted)
                continue
            if authorised:
                if self.bot.pseudo2role(toMute) == "moderator":
                    rapport = "On ne peut pas muter quelqu'un ayant des droits aussi élevés\n"
                else:
                    t = Timer(30.0, lambda name=toMute : self.restore(name)) 
                    t.start()
                    if orNot:
                        modules.utils.mute(toMute,random.choice(reasonfail)%(toMute),self.bot)
                    else:
                        modules.utils.mute(toMute,random.choice(reasonkick)%(toMute),self.bot)
        return rapport[:-1]

class FakeBot:
    """Pour les tests unitaires"""
    def __init__(self):
        self.name = "lebot"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    b = FakeBot()
    o = CmdMute(b)
    print o.answer('xouillet', 'Bad Company')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdMute)

