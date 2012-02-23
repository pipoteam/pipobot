#! /usr/bin/env python
#-*- coding: utf-8 -*-

import random
import urllib
import lib.utils
import re
from BeautifulSoup import BeautifulSoup
from lib.modules import SyncModule, answercmd

class CmdVdm(SyncModule):
    def __init__(self, bot):
        desc = """Pour afficher des vdm.
vdm : Retourne une vdm aléatoire.
vdm [n] : Affiche la vdm [n]"""
        SyncModule.__init__(self,
                            bot,  
                            desc = desc,
                            command = "vdm",
                            lock_time = 2,
                            )

    #################################################################
    #            PARSING ARGS                                       #
    #################################################################

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        """!vdm [n]"""
        index = message.groupdict()["index"]
        page = urllib.urlopen('http://www.viedemerde.fr/travail/%s'%(index))
        return CmdVdm.get_vdm(page)


    @answercmd(r"^$")
    def answer(self, sender, message):
        """!vdm"""
        page = 'http://www.viedemerde.fr/aleatoire'
        return CmdBashfr.get_vdm(page)

    #################################################################
    #            LIB                                                #
    #################################################################

    @staticmethod
    def get_vdm(url):
        url = urllib.urlopen(url)
        contenu = url.read()
        tmp = contenu.partition('<div class="post article" id="')[2]
        res = tmp.partition(">")[2].partition("VDM")[0]
        nb =  tmp.partition('"')[0]
        res = "VDM#%s : %sVDM"%(nb, res)
        return lib.utils.xhtml2text(res)
