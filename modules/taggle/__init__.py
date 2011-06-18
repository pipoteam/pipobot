#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import time
import threading
import random
sys.path.append("modules/mpd")
from lib.BotMPD import BotMPD

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")


class CmdTaggle:
    def __init__(self, bot):
        self.bot = bot
        self.command = "tg"
        self.desc = "Ta gueule [nom]\nDit taggle à nom (avec Fabien par défaut bien sûr :p)"
        self.pm_allowed = True
            
    def answer(self, sender, message):
        if sender.lower() == "fabien" and message == '':
            toalmostall = []
            for people in self.bot.jids.iterkeys():
                if self.bot.jid2pseudo(people) != self.bot.name:
                    if self.bot.jid2pseudo(people) != sender:
                        toalmostall.append(self.bot.jid2pseudo(people))
            return "%s: Fermez tous voggle !!!"%(" ".join(toalmostall))
        else:
            if message == '':
                return "Taggle Fabien"
            elif self.bot.name.lower() in message.lower():
                r = random.random()
                if r < 0.1:
                    self.bot.say("Ouais ouais et puis quoi encore ?!")
                else:
                    self.bot.say("Bon bah puisque c'est comme ça je boude")
                    self.bot.mute = True
                    self.bot.t = threading.Timer(30.0, self.bot.disable_mute)
                    self.bot.t.start()
                return ""
            elif message.lower() == sender.lower():
                return "Non mais vraiment ... taggle ! Au lieu de me faire dire n'importe quoi !"
            else:
                b = BotMPD(config.HOST, config.PORT, config.PASSWORD)
                current = b.current()
                if "(" in message:
                    message, reason = message.split("(", 2)
                else:
                    reason = ""
                if 'aveugle' in message:
                    if 'ontagn' in current:
                        b.next()
                        return "Oui oui, taggle l'aveugle !!!"
                elif message in current:
                    b.next()
                    if reason != "":
                        return "%s: %s"%(message, reason.partition(")")[0])
                else:
                    return "Taggle %s" % message

class FakeBot:
    """Pour les tests unitaires"""
    def __init__(self):
        self.name = "lebot"

if __name__ == '__main__':
    #Unitary tests
    b = FakeBot()
    o = CmdTaggle(b)
    print o.answer('xouillet', 'Bad Company')    
    print o.answer('xouillet', '')    
else:
    from .. import register
    register(__name__, CmdTaggle)

