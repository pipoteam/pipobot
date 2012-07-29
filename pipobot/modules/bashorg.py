#! /usr/bin/env python
#-*- coding: utf-8 -*-

import pipobot.lib.utils
from BeautifulSoup import BeautifulSoup
from pipobot.lib.abstract_modules import FortuneModule

class CmdBashorg(FortuneModule):
    def __init__(self, bot):
        desc = """To read quotes from bash.org
bashorg : Returns a random quote from bash.org.
bashorg [n] : Show the quote [n] from bash.org"""
        FortuneModule.__init__(self,
                        bot,  
                        desc = desc,
                        command = "bashorg",
                        url_random = "http://bash.org/?random",
                        url_indexed = 'http://bash.org/?quote=%s',
                        lock_time = 2,
                        )


    def extract_data(self, html_content):
        soup = BeautifulSoup(html_content)
        sections = soup.findAll("p", { "class": "qt" })
        centers = soup.findAll("center")
        if sections == []:
            return "The quote does not exist !"

        tables = soup.findAll("table")
        for elt in tables:
            p = elt.findAll("p", {"class": "qt"})
            if p != []:
                content = pipobot.lib.utils.xhtml2text(unicode(p[0]))
                nb = pipobot.lib.utils.xhtml2text(unicode(elt.findAll("b")[0].text))
                break

        return "%s :\n %s"%(nb, content)
