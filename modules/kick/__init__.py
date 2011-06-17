#! /usr/bin/env python
#-*- coding: utf-8 -*-
import xmpp
import random
import modules.utils

class CmdKick:
    def __init__(self, bot):
        self.bot = bot
        self.command = "kick"
        self.desc = "kick [nom]\nKick quelqu'un du salon !"
        self.pm_allowed = True
            
    def answer(self, sender, message):
        role_sender = self.bot.pseudo2role(sender)
        reasonfail = ["%s: TPPT !!!",
                      "%s: Je n'obéis qu'au personnel compétent",
                      "%s: Tu crois vraiment que je vais t'obéir",
                      "%s: Non mais tu te crois où ? oO",
                      "%s: J'vais l'dire aux modérateurs"]
        reasonkick = ["Au revoir %s",
                      "Désolé %s, je ne fais qu'obéir aux ordres"]

        lst = message.split(" ")
        rapport = ""
        for kicked in lst:
            authorised = False
            orNot = False
            if kicked == self.bot.name:
                rapport += "Je vais pas me virer moi-même oO\n"
                continue
            try:
                jidkicked = self.bot.pseudo2jid(kicked)
                jidsender = self.bot.pseudo2jid(sender)
                if jidkicked == jidsender:
                    if kicked == sender:
                        rapport += "Tu veux te virer toi-même ?\n"
                    else:
                        authorised = True
                        toKick = kicked
                        rapport += "j'ai viré %s à la demande de %s car il semblerait que ce soit un imposteur\n"%(kicked, sender)
                elif role_sender != "moderator":
                    orNot = True
                    authorised = True
                    toKick = sender
                    rapport += "%s n'a pas le droit de virer %s\n"%(sender, kicked)
                else:
                    authorised = True
                    toKick = kicked
                    rapport += "j'ai viré %s pour toi !\n"%(kicked)
                    
            except:
                rapport += "%s n'est pas dans le salon\n"%(kicked)
                continue
            if authorised:
                if self.bot.pseudo2role(toKick) == "moderator":
                    rapport = "On ne peut pas kicker quelqu'un ayant des droits aussi élevés\n"
                else:
                    if orNot:
                        modules.utils.kick(toKick,random.choice(reasonfail)%(toKick),self.bot)
                    else:
                        modules.utils.kick(toKick,random.choice(reasonkick)%(toKick),self.bot)


        return rapport[:-1]

class FakeBot:
    """Pour les tests unitaires"""
    def __init__(self):
        self.name = "lebot"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    b = FakeBot()
    o = CmdKick(b)
    print o.answer('xouillet', 'Bad Company')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdKick)

