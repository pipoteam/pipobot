#! /usr/bin/env python
#-*- coding: utf-8 -*-

import pipobot.lib.utils
from pipobot.lib.abstract_modules import FortuneModule

class CmdVdm(FortuneModule):
    def __init__(self, bot):
        desc = """Pour afficher des vdm.
vdm : Retourne une vdm aléatoire.
vdm [n] : Affiche la vdm [n]"""
        FortuneModule.__init__(self,
                            bot,  
                            desc = desc,
                            command = "vdm",
                            url_random = "http://www.viedemerde.fr/aleatoire",
                            url_indexed = "http://www.viedemerde.fr/travail/%s",
                            lock_time = 2,
                            )

    def extract_data(self, soup):
        a = soup.findAll("div", {"class" : "post article"})[0].findAll("a")[0]
        nb = a.get("href").split("/")[-1]
        content = a.text
        res = "VDM#%s : %s VDM"%(nb, content)
        return pipobot.lib.utils.xhtml2text(res)
