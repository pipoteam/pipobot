#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import repartie
import re
import modules.utils

class CmdBot:
    def __init__(self, bot):
        self.bot = bot
            
    def answer(self, sender, message):
        if type(message) not in (str, unicode):
            return
        if message == "":
            return
        if message[0] == "!":
            return
        if re.search("^"+self.bot.name.lower()+"(\W|$)", message.lower()):
            if '?' in message:
                d = repartie.question.split("\n")
            else:
                d = repartie.direct.split("\n")
            random.shuffle(d)
            return "%s: %s"%(sender, d[0])
        elif re.search("(^|\W)"+self.bot.name.lower()+"($|\W)", message.lower()):
            i = repartie.indirect.split("\n")
            random.shuffle(i)
            return "%s: %s"%(sender, i[0])
        elif re.search("(\s|^)+si\s+ils(\s|$)+", message.lower()):
            return "%s: S'ILS, c'est mieux !!! :@"%(sender)
        elif re.search("(\s|^)+si\s+il(\s|$)+", message.lower()):
            return "%s: S'IL, c'est mieux !!!"%(sender)
        elif re.search("(^|\s)+_all_(\!|\?|\:|\s+|$)", message.lower()):
            if self.bot.pseudo2role(self.bot.name) == "moderator":
                reply = ", ".join(["%s"%(people) for people in self.bot.jids.iterkeys() if self.bot.pseudo2jid(people) not in [self.bot.pseudo2jid(sender), self.bot.pseudo2jid(self.bot.name)]])
            else:
                reply = ", ".join(["%s"%(people) for people in self.bot.droits.iterkeys() if self.bot.jid2pseudo(people) not in [sender, self.bot.name]])
            message = message.replace("_all_", reply)
            return message
        l = [["server", "serveur", "bot"], ["merde", "bois", "carton"]]
        if all([any([elt2 in message.lower() for elt2 in elt]) for elt in l]):
            msg = "Tu sais ce qu'il te dit le serveur ? Et puis surveille ton langage d'abord !!!"
            modules.utils.kick(sender, msg, self.bot)

class FakeBot:
    def __init__(self):
        self.name = "Pipo-test"

if __name__ == '__main__':
    #Placer ici les tests unitaires
    bot = FakeBot()
    c = CmdBot(bot)
    print c.answer("qsfd", "Pipo-test: est un connard")
    pass
else:
    from .. import register
    register(__name__, CmdBot)

