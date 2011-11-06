#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import threading
import lib.utils
from BeautifulSoup import BeautifulSoup
import lib.modules.SyncModule 

class CmdBashfr(lib.modules.SyncModule):
    def __init__(self, bot):
        desc = """Pour lire des quotes bashfr
bashfr : Retourne une quote aléatoire de bashfr.
bashfr [n] : Affiche la quote [n] de bashfr"""
        lib.modules.SyncModule.__init__(bot, 
                        desc = desc,
                        command = "bashfr",
                        )
        self.bot.bashfrlock = False

    def enable(self):
        self.bot.bashfrlock = False
            
    @answercmd()
    def answer(self, sender, message):
        if self.bot.bashfrlock:
            return "Attends un peu !!"
        self.bot.bashfrlock = True
        t = threading.Timer(5, self.enable)
        t.start()
        if (not message.strip()):
            url = urllib.urlopen('http://danstonchat.com/random.html')
        if (not message.strip()):
            url = urllib.urlopen('http://danstonchat.com/random.html')
        elif message.isdigit():
            url = urllib.urlopen('http://danstonchat.com/%s.html'%(message))
        else:
            return "Utilise un entier si tu veux une quote spécifique, ou rien si tu préfères aller à Toire"
        contenu = url.read()
        soup = BeautifulSoup(contenu)
        if soup.find("h2", text = "Erreur 404"):
            return "La quote demandée n'existe pas. (Erreur 404)"
        else:
            sections = soup.findAll("p", { "class": "item-content" })
            choiced = random.randrange(len(sections))
            tableau = sections[choiced].a.contents
            if message.isdigit():
                nb = message
            else:
                nb = sections[choiced].a["href"].partition("/")[2].partition(".")[0]
            x = u""
            for i in tableau:
                if unicode(i) == u"<br />":
                    x += "\n"
                    pass
                else:
                    x = x + lib.utils.xhtml2text(unicode(i))
            return "bashfr #%s :\n%s"%(nb, x)
