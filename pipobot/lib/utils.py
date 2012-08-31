#! /usr/bin/python
#-*- coding: utf-8 -*-

import re
import xmpp
import utils
import urllib
import httplib
import htmlentitydefs
from BeautifulSoup import BeautifulSoup, SoupStrainer
from HTMLParser import HTMLParseError

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def xhtml2text(html):
#fonction de conversion xHTML -> texte pour les clients
#ne supportant pas la XEP-0071
    # on symbolise le gras par "*"
    html = re.sub('<[^>]*b>', '*', html)
    html = re.sub('<[^>]*strong>', '*', html)
    # le souligné par "_"
    html = re.sub('<[^>]*u>', '_', html)
    # on enlève toutes les autres balises
    #TODO: récuppérer le lien dans les balises <a>
    html = re.sub('<[^>]*>', '', html)

    return unescape(html)


def kick(toKick, msg, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns", "http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toKick)
    itemchild.setAttr("role", "none")

    reason = itemchild.addChild("reason")
    reason.addData(msg)
    bot.send(iq)


def mute(toKick, msg, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns", "http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toKick)
    itemchild.setAttr("role", "visitor")
    reason = itemchild.addChild("reason")
    reason.addData(msg)
    bot.send(iq)


def unmute(toMute, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns", "http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toMute)
    itemchild.setAttr("role", "participant")
    bot.send(iq)


class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = ("Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+"
               "(KHTML, like Gecko) Safari/531.2+ Midori/0.2")
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
                SoupList = BeautifulSoup(utils.unescape(html),
                                         parseOnlyThese=SoupStrainer('title'))
            except UnicodeDecodeError:
                SoupList = BeautifulSoup(utils.unescape(html.decode("latin1", "ignore")),
                                         parseOnlyThese=SoupStrainer('title'))
            try:
                titles = [title for title in SoupList]
                title = utils.xhtml2text(titles[0].renderContents())
            except IndexError:
                title = "Pas de titre"
            except HTMLParseError:
                pass
            if geturl:
                send.append("%s : [Lien] Titre : %s" %
                            (o.geturl(), " ".join(title.split())))
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
