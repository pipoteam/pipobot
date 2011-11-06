#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import threading
import lib.utils
from BeautifulSoup import BeautifulSoup

class CmdBashorg:
    def __init__(self, bot):
        self.bot = bot
        self.command = "bashorg"
        self.desc = """To read quotes from bash.org
bashorg : Returns a random quote from bash.org.
bashorg [n] : Show the quote [n] from bash.org"""
        self.pm_allowed = True
        self.bot.bashorglock = False

    def enable(self):
        self.bot.bashorglock = False
            
    def answer(self, sender, message):
        if self.bot.bashfrlock:
            return "Please do not flood !"
        self.bot.bashorglock = True
        t = threading.Timer(5, self.enable)
        t.start()
        if (not message.strip()):
            url = urllib.urlopen('http://bash.org/?random')
        elif message.isdigit():
            url = urllib.urlopen('http://bash.org/?%s'%(message))
        else:
            return self.desc
        contenu = url.read()
        soup = BeautifulSoup(contenu)
        sections = soup.findAll("p", { "class": "qt" })
        centers = soup.findAll("center")
        if sections == []:
            return "The quote does not exist !"

        tables = soup.findAll("table")
        for elt in tables:
            p = elt.findAll("p", {"class": "qt"})
            if p != []:
                content = lib.utils.xhtml2text(unicode(p[0]))
                nb = lib.utils.xhtml2text(unicode(elt.findAll("b")[0].text))
                break

        return "%s :\n %s"%(nb, content)

class FakeBot:
    def __init__(self):
        self.bashfrlock = False


if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdBashorg(FakeBot())
    print o.answer('pipo', '')
else:
    from .. import register
    register(__name__, CmdBashorg)

