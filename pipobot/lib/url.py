#! /usr/bin/env python
#-*- coding: utf-8 -*-
import utils
import urllib
import httplib
from BeautifulSoup import BeautifulSoup, SoupStrainer
from HTMLParser import HTMLParseError


class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()


def check_url(url, geturl=False):
    send = []
    try:
        o = urllib.urlopen(url)
        ctype, clength = o.info().get("Content-Type"), o.info().get("Content-Length")
        if  o.info().gettype() == "text/html":
            title = 'Pas de titre'
            html = o.read(1000000)
            try:
                SoupList = BeautifulSoup(utils.unescape(html), parseOnlyThese=SoupStrainer('title'))
            except UnicodeDecodeError:
                SoupList = BeautifulSoup(utils.unescape(html.decode("latin1", "ignore")), parseOnlyThese=SoupStrainer('title'))
            try:
                titles = [title for title in SoupList]
                title = utils.xhtml2text(titles[0].renderContents())
            except IndexError:
                title = "Pas de titre"
            except HTMLParseError:
                pass
            if geturl:
                send.append("%s : [Lien] Titre : %s" % (o.geturl(), " ".join(title.split())))
            else:
                send.append("[Lien] Titre : %s" % " ".join(title.split()))
        else:
            send.append("[Lien] Type: %s, Taille : %s octets" % (ctype, clength))
        o.close()
    except IOError as error:
        if error[1] == 401:
            send.append("Je ne peux pas m'authentifier sur %s :'(" % url)
        elif error[1] == 404:
            send.append("%s n'existe pas !" % url)
        elif error[1] == 403:
            send.append("Il est interdit d'accéder à %s !" % url)
        else:
            send.append("Erreur %s sur %s" % (error[1], url))
    except httplib.InvalidURL:
        send.append("L'URL %s n'est pas valide !" % url)
    return send
