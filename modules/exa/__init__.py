#! /usr/bin/env python
#-*- coding: utf-8 -*-

import BeautifulSoup
import urllib
import urllib2
import re

class CmdExa:
    def __init__(self, bot):
        self.bot = bot
        self.command = "exa"
        self.desc = "exa [mots clefs]\nEffectue une recherche sur le web et affiche les 4 premiers résultats"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        # Définir le nombre MAX de résultats à retourner
        limite = 4

        motclef = message
        motclef = motclef.encode("utf8")

        # Converti les mots clefs pour l'url
        valeurs = {'q': motclef}
        motclef = urllib.urlencode(valeurs)
        url = 'http://exalead.fr/search/web/results/?'+motclef
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept-Language', 'fr')]
        result = opener.open(url)
        body = BeautifulSoup.BeautifulSoup(result.read())

        # Verifie qu'on recuppère bien des résultats
        try:
            nbre_results = len(body.find('ol', id="results").contents) / 2
        except:
            nbre_results = -1

        if nbre_results > 1:
            results = []
            for i in range( min([nbre_results, limite] )):
                results.append(body.find('ol', id="results").contents[2*i+1].contents[3].contents[1].contents[1])
            # Fabrication de la sortie suivant le mode désiré
            redir = u""
            redir_xhtml = u""
            for i in range( min([nbre_results, limite]) ):
                    redir += "\n " + results[i]['href'] + u" --- " + results[i]['title'] 
                    redir_xhtml += u"\n<br/> <a href=\"" + results[i]['href'] + u"\" alt=\"" + results[i]['href'] + u"\">" + results[i]['title'] + u"</a>"
        else:   
            redir = u"Pas de résultat"
            redir_xhtml = ""

        return (redir, redir_xhtml)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdExa(None)
    print o.answer('pipo', '')   
    print "\n\n "
    print o.answer('pipo', 'sexe')    
else:
    from .. import register
    register(__name__, CmdExa)

