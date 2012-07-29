#! /usr/bin/env python
#-*- coding: utf-8 -*-

import pipobot.lib.utils
from BeautifulSoup import BeautifulSoup
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

    def extract_data(self, html_content):
        soup = BeautifulSoup(html_content)
        res = []
        a = soup.find("div", {"class" : "post article"}).find("p")#.findAll("a")[0]
        for elt in a.findAll("a"):
            res.append(pipobot.lib.utils.xhtml2text(elt.text))
        nb = a.findAll("a")[0].get("href").split("/")[-1]
        res = "VDM#%s : %s"%(nb, "".join(res))
        return res
