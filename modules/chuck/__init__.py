#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import lib.utils
import re
from BeautifulSoup import BeautifulSoup
from lib.modules import SyncModule, answercmd 

class CmdChuck:
    def __init__(self, bot):
        desc = """Pour afficher des chucknorrisfact.
chuck : Retourne un fact aléatoire.
chuck [n] : Affiche le fact [n]"""
        SyncModule.__init__(self, 
                            bot,  
                            desc = desc,
                            command = "chuck",
                            )

    @answercmd
    def answer(self, sender, message):
        if (not message.strip()):
            url = urllib.urlopen('http://www.chucknorrisfacts.fr/index.php?p=parcourir&tri=aleatoire')
            byid = False
        elif message.isdigit():
            url = urllib.urlopen('http://www.chucknorrisfacts.fr/index.php?p=detail_fact&fact=%s' % (message))
            byid = True
        else:
            return "Utilise un entier si tu veux une quote spécifique, ou rien si tu préfères aller à Toire"
        contenu = url.read()
        soup = BeautifulSoup(contenu)
        fact = soup.findAll("div", {"class": "fact"})[0]
        index = fact.get("id").partition("fact")[2]
        content = lib.utils.xhtml2text(fact.text)
        return "Fact #%s : %s"%(index, content)
