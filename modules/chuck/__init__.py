#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import lib.utils
import re
from BeautifulSoup import BeautifulSoup
from lib.modules import SyncModule, answercmd

class CmdChuck(SyncModule):
    def __init__(self, bot):
        desc = """Pour afficher des chucknorrisfact.
chuck : Retourne un fact aléatoire.
chuck [n] : Affiche le fact [n]"""
        SyncModule.__init__(self, 
                            bot,  
                            desc = desc,
                            command = "chuck",
                            lock_time = 2,
                            )

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        """!chuck [n]"""
        index = message.group("index")
        page = 'http://www.chucknorrisfacts.fr/index.php?p=detail_fact&fact=%s' % (index)
        return CmdChuck.get_chuck(page)

    @answercmd(r"^$")
    def answer(self, sender, message):
        """!chuck"""
        page = 'http://www.chucknorrisfacts.fr/index.php?p=parcourir&tri=aleatoire'
        return CmdChuck.get_chuck(page)

    @staticmethod
    def get_chuck(url):
        url = urllib.urlopen(url)
        contenu = url.read()
        soup = BeautifulSoup(contenu)
        fact = soup.findAll("div", {"class": "fact"})[0]
        index = fact.get("id").partition("fact")[2]
        content = lib.utils.xhtml2text(fact.text)
        return "Fact #%s : %s"%(index, content)
