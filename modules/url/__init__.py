#! /usr/bin/env python
#-*- coding: utf-8 -*-
import re
import xmpp
import urllib
import modules.utils
import httplib
from BeautifulSoup import BeautifulSoup, SoupStrainer
from HTMLParser import HTMLParseError

class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()


class CmdUrl:
    def __init__(self, bot):
        self.bot = bot
            
    def answer(self, sender, message):
        if type(message) not in (str, unicode):
            return

        send = []
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-/_=?:;]|[!*\(\),~@]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        for url in urls:
            try:
                o=urllib.urlopen(url)
                ctype, clength = o.info().get("Content-Type"), o.info().get("Content-Length")
                if  o.info().gettype() == "text/html":
                    title = 'Pas de titre'
                    html = o.read(1000000)
                    try:
                        SoupList = BeautifulSoup(modules.utils.unescape(html), parseOnlyThese=SoupStrainer('title'))
                    except UnicodeDecodeError:
                        SoupList = BeautifulSoup(modules.utils.unescape(html.decode("latin1", "ignore")), parseOnlyThese=SoupStrainer('title'))
                    try:
                        titles = [title for title in SoupList]
                        title = modules.utils.xhtml2text(titles[0].renderContents())
                    except IndexError:
                        title = "Pas de titre"
                    except HTMLParseError:
                        pass
                    send.append("[Lien] Titre : %s" % " ".join(title.split()))
                else:
                    send.append("[Lien] Type: %s, Taille : %s octets" % (ctype, clength))
                o.close()
            except IOError as error:
                if error[1] == 401:
                    send.append("Je ne peux pas m'authentifier sur ce site :''(")
                elif error[1] == 404:
                    send.append("Cette page n'existe pas !")
                elif error[1] == 403:
                    send.append("Il est interdit d'accéder à cette page !")
                else:
                    send.append("Erreur %s sur cette page"%(error[1]))
            except httplib.InvalidURL:
                send.append("L'URL n'est pas valide !")

        return None if send == [] else "\n".join(send)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    url = CmdUrl(None)
    print url.answer("xouillet","http://www.bde.enseeiht.fr/services/sondages/date-de-la-reunion-net7/")
    print url.answer("xouillet","http://mpd:qsdfqsf@mpd.sleduc.fr/")
else:
    from .. import register
    register(__name__, CmdUrl)

