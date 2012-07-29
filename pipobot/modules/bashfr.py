#! /usr/bin/env python
#-*- coding: utf-8 -*-

import random
import pipobot.lib.utils
from BeautifulSoup import BeautifulSoup
from pipobot.lib.abstract_modules import FortuneModule

class CmdBashfr(FortuneModule):
    def __init__(self, bot):
        desc = """Pour lire des quotes bashfr
bashfr : Retourne une quote aléatoire de bashfr.
bashfr [n] : Affiche la quote [n] de bashfr"""
        FortuneModule.__init__(self,
                        bot,  
                        desc = desc,
                        command = "bashfr",
                        url_random = "http://danstonchat.com/random.html",
                        url_indexed = 'http://danstonchat.com/%s.html',
                        lock_time = 2,
                        )

    def extract_data(self, html_content):
        soup = BeautifulSoup(html_content)
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
                    result = result + pipobot.lib.utils.xhtml2text(unicode(i))
            return "bashfr #%s :\n%s"%(nb, result)
