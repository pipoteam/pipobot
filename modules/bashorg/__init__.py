#! /usr/bin/env python
#-*- coding: utf-8 -*-
import random
import urllib
import threading
import lib.utils
from BeautifulSoup import BeautifulSoup
from lib.modules import SyncModule, defaultcmd, answercmd

class CmdBashorg(SyncModule):
    def __init__(self, bot):
        desc = """To read quotes from bash.org
bashorg : Returns a random quote from bash.org.
bashorg [n] : Show the quote [n] from bash.org"""
        SyncModule.__init__(self, bot,  
                        desc = desc,
                        command = "bashorg",
                        lock_time = 2,
                        )

    #################################################################
    #            PARSING ARGS                                       #
    #################################################################

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        """!bashorg [n]"""
        index = message.groupdict()["index"]
        page = 'http://bash.org/?quote=%s' % (index)
        return CmdBashorg.get_bashorg(page)


    @answercmd(r"^$")
    def answer_empty(self, sender, message):
        """!bashorg"""
        page = 'http://bash.org/?random'
        return CmdBashorg.get_bashorg(page)


    #################################################################
    #            LIB                                                #
    #################################################################

    @staticmethod
    def get_bashorg(url):
        url = urllib.urlopen(url)
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
