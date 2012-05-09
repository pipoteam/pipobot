#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import repartie
import re
from pipobot.lib.modules import ListenModule
from pipobot.lib import utils

class CmdBot(ListenModule):
    def __init__(self, bot):
        desc = "The bot will not let you say anything about him !!"
        ListenModule.__init__(self, bot,  name = "repartie", desc = desc)

    def answer(self, sender, message):
        if type(message) not in (str, unicode):
            return
        if message == "":
            return
        if message[0] in ["!", ":"]:
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
            reply = self.bot.occupants.get_all(", ", [sender, self.bot.name]) 
            message = message.replace("_all_", reply)
            return message
        l = [["server", "serveur", "bot"], ["merde", "bois", "carton"]]
        if all([any([elt2 in message.lower() for elt2 in elt]) for elt in l]):
            msg = "Tu sais ce qu'il te dit le serveur ? Et puis surveille ton langage d'abord !!!"
            utils.kick(sender, msg, self.bot)
