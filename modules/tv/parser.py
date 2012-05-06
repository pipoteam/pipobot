#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
from pipobot.lib.utils import xhtml2text

class requete:
    SOIREE = ("contenu grille grilleprimes grillehome", "http://www.programme-tv.net")
    TNT = ("contenu grille grilleprimes", "http://www.programme-tv.net/programme/programme-tnt.html")
#    SOIREE = ("contenu grille grilleprimes grillehome","/home/seb/Downloads/soiree.html")
#    TNT = ("contenu grille grilleprimes","/home/seb/Downloads/TNT.html")

def extract(divclasse,LOCAL = False):
    if LOCAL:
        f = open(divclasse[1])
    else:
       f = urllib.urlopen(divclasse[1]) 
    content = f.read()
    f.close()
    soup = BeautifulSoup(content)
    grid = soup.findAll("div", {"class": divclasse[0]})
    res = {}
    for elt in grid:
        for eltli in elt.findAll("li"):
            chaine = eltli.first("span", {"class":"txtLogoChaine"})
            try:
                chaine = chaine.getText().partition("Programme ")[2]
            except AttributeError:
                continue
            soiree = ""    
            for eltp in eltli.findAll("p"):
                a = eltp.findAll("a")
                try:
                    title = a[0].get("title")
                except IndexError:
                    continue
                span = eltp.findAll("span")
                hour = span[0].getText()
                soiree += "%s : %s "%(hour, title)
            chaine = xhtml2text(chaine).lower()
            soiree = xhtml2text(soiree)
            res[chaine] = soiree
    return res
    
if __name__ == "__main__":
    print extract(requete.SOIREE,False)
    print extract(requete.TNT,False)
