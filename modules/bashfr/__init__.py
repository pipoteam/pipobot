#! /usr/bin/env python
#-*- coding: utf-8 -*-

import random
import urllib
import threading
import lib.utils
from BeautifulSoup import BeautifulSoup
from lib.modules import SyncModule, defaultcmd, answercmd

class CmdBashfr(SyncModule):
    def __init__(self, bot):
        desc = """Pour lire des quotes bashfr
bashfr : Retourne une quote aléatoire de bashfr.
bashfr [n] : Affiche la quote [n] de bashfr"""
        SyncModule.__init__(self, 
                        bot,  
                        desc = desc,
                        command = "bashfr",
                        lock_time = 2,
                        )

    #################################################################
    #            PARSING ARGS                                       #
    #################################################################

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        """!bashfr [n]"""
        index = message.groupdict()["index"]
        page = 'http://danstonchat.com/%s.html'%(index)
        return CmdBashfr.get_bashfr(page)


    @answercmd(r"^$")
    def answer(self, sender, message):
        """!bashfr"""
        page = 'http://danstonchat.com/random.html'
        return CmdBashfr.get_bashfr(page)

    #################################################################
    #            LIB                                                #
    #################################################################

    @staticmethod
    def get_bashfr(url):
        page = urllib.urlopen(url)
        contenu = page.read()
        page.close()
        soup = BeautifulSoup(contenu)
        if soup.find("h2", text = "Erreur 404"):
            return "La quote demandée n'existe pas. (Erreur 404)"
        else:
            sections = soup.findAll("p", { "class": "item-content" })
            choiced = random.randrange(len(sections))
            tableau = sections[choiced].a.contents
            nb = sections[choiced].a["href"].partition("/")[2].partition(".")[0]
            result = u""
            for i in tableau:
                if unicode(i) == u"<br />":
                    result += "\n"
                    pass
                else:
                    result = result + lib.utils.xhtml2text(unicode(i))
            return "bashfr #%s :\n%s"%(nb, result)
