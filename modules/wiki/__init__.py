#! /usr/bin/env python
#-*- coding: utf-8 -*-

import BeautifulSoup
import urllib
import urllib2
import re
 
class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()

class CmdWiki:
    def __init__(self, bot):
        self.bot = bot
        self.command = "wiki"
        self.desc = "wiki [mots clefs]\nEffectue une recherche sur wikipedia"
	self.pm_allowed = True
            
    def answer(self, sender, message):
        motclef = message
        motclef = motclef.encode("utf8")

        # Converti les mots clefs pour l'url
        url = 'http://fr.wikipedia.org/wiki/'+motclef
        opener = urllib.urlopen(url)
        opener.addheaders = [('Accept-Language', 'fr')]
        no_results = False
        
        # Verifie qu'on recuppère bien des résultats

        if no_results == False:
            redir = u""
            redir_xhtml = u""
            redir += url + u" --- " + motclef
            redir_xhtml += u"\n<br/> <a href=\"" + url + u"\" alt=\"" + url + u"\">" + motclef + u"</a> " 
        else:   
            redir = u"Pas de résultat"
            redir_xhtml = "Pas de résultat"

        return (redir, redir_xhtml)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdWiki(None)
    print o.answer('pipo', 'entreprise')    
else:
    from .. import register
    register(__name__, CmdWiki)

