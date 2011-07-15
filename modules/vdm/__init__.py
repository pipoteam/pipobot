#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import modules.utils
import re
from BeautifulSoup import BeautifulSoup

class CmdVdm:
    def __init__(self, bot):
        self.bot = bot
        self.command = "vdm"
        self.desc = """Pour afficher des vdm.
vdm : Retourne une vdm aléatoire.
vdm [n] : Affiche la vdm [n]"""
        self.pm_allowed = True

    def answer(self, sender, message):
        if (not message.strip()):
            url = urllib.urlopen('http://www.viedemerde.fr/aleatoire')
            byid = False
        elif message.isdigit():
            url = urllib.urlopen('http://www.viedemerde.fr/travail/%s'%(message))
            byid = True
        else:
            return "Utilise un entier si tu veux une quote spécifique, ou rien si tu préfères aller à Toire"
        contenu = url.read()
        if byid:
            res = contenu.partition('<div class="post article" id="')[2].partition("VDM")[0].partition("<p>")[2].partition("VDM")[0]
            nb = message
        else:
            tmp = contenu.partition('div class="post article" id="')[2]
            res = tmp.partition(">")[2].partition("VDM")[0]
            nb =  tmp.partition('"')[0]
        res = "VDM#%s : %sVDM"%(nb, res)
        return modules.utils.xhtml2text(res)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdVdm(None)
    print o.answer('pipo', '')
else:
    from .. import register
    register(__name__, CmdVdm)

