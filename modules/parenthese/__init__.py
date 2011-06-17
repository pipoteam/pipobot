#! /usr/bin/env python
#-*- coding: utf-8 -*-
import re
import random
import modules.utils

class CmdParanthese :
    def __init__(self,bot) :
        self.bot = bot
            
    def answer(self, sender, message) :
        if type(message) not in (str,unicode) :
            return

        send = ""
        po = message.count("(")
        pf = message.count(")")
        nbsf = len(re.findall("((^|\s)+\W|(^|\s)+[xX])\)", message))
        nbso = len(re.findall("((^|\s)+\W|(^|\s)+[xX])\(", message))
        #nbsf = len(re.findall("([^A-Za-z0-9 !\?\.\)\(]\)| [xX]\))", message))
        #nbso = len(re.findall("([^A-Za-z0-9 !\?\.\)\(]\(| [xX]\()", message))
        nb = po - nbso - pf + nbsf
        listS = ["Fail de parenthèses !", "On fait pas de la merde dans les parenthèses !",
            "Et les parenthèses c'est pour les chiens ?!"]
        if nb > 0:
            listSp = listS[:]+["Ferme la parenthèse et ta gueule avec !", "Ferme la parenthèse et la porte en sortant."]
            send = sender + ": " + random.choice(listSp)
        elif nb < 0:
            listSn = listS[:]+["Il faut l'ouvrir pour la fermer..."]
            send = sender + ": " + random.choice(listSn)
        return None if send == [] else send

if __name__ == '__main__' :
    #Placer ici les tests unitaires
    pass
else :
    from .. import register
    register(__name__,CmdParanthese)

