#! /usr/bin/env python
#-*- coding: utf-8 -*-
import re
import xmpp
import urllib
import pipobot.lib.utils
import httplib
import sqlalchemy.exc
from BeautifulSoup import BeautifulSoup, SoupStrainer
from HTMLParser import HTMLParseError
from pipobot.lib.modules import ListenModule
from model import RepostUrl

try:
    from hyperlinks_scanner import HyperlinksScanner
except ImportError:
    HyperlinksScanner = None


URLS_RE = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-/_=?:;]|[!*\(\),~@]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()


class CmdUrl(ListenModule):
    def __init__(self, bot):
        desc = "Extracting title of page from URL"
        ListenModule.__init__(self, bot,  name = "url", desc = desc)
        settings = self.bot.settings
        try:
            self.repost = settings['modules']['url']['repost']
        except KeyError:
            self.repost = False
        try:
            self.repost_ignore = settings['modules']['url']['repost-ignore']
        except KeyError:
            self.repost_ignore = []

    def answer(self, sender, message):
        if HyperlinksScanner:
            scanner = HyperlinksScanner(message, strict=True)
            urls = set([link.url for link in scanner])
        else:
            urls = set(URLS_RE.findall(message))

        try:
            repost_msg = self.check_repost(sender, urls)
        except sqlalchemy.exc.OperationalError:
            self.bot.session.rollback()
            repost_msg = []
        except sqlalchemy.exc.InvalidRequestError:
            repost_msg = []

        title_page = self.get_title(urls)
        send = repost_msg + title_page
        return None if send == [] else "\n".join(send)

    def check_repost(self, sender, urls):
        send = []
        if self.repost:
            for url in urls:
                if not any(i in url for i in self.repost_ignore):
                    res = self.bot.session.query(RepostUrl).filter(RepostUrl.url == url).first()
                    if res:
                        send.append('OLD! ')
                        first = ''
                        try:
                            first = self.bot.occupants.jid_to_pseudo(res.jid)
                        except KeyError:
                            first = res.jid
                        first_date = 'le ' + res.date.strftime('%x') + ' à ' + res.date.strftime('%X')
                        if res.count == 1:
                            send.append('Ce lien a déjà été posté %s par %s… '%(first_date,first))
                        else:
                            send.append('Ce lien a déjà été posté %s fois depuis que %s l’a découvert, %s… ' % (res.count,first,first_date))
                        res.count += 1
                    else:
                        u = RepostUrl(url, self.bot.occupants.pseudo_to_jid(sender))
                        self.bot.session.add(u)
                        self.bot.session.commit()
        return send

    def get_title(self, urls):
        send = []
        for url in urls:
            try:
                o=urllib.urlopen(url)
                ctype, clength = o.info().get("Content-Type"), o.info().get("Content-Length")
                if  o.info().gettype() == "text/html":
                    title = 'Pas de titre'
                    html = o.read(1000000)
                    try:
                        SoupList = BeautifulSoup(pipobot.lib.utils.unescape(html), parseOnlyThese=SoupStrainer('title'))
                    except UnicodeDecodeError:
                        SoupList = BeautifulSoup(pipobot.lib.utils.unescape(html.decode("latin1", "ignore")), parseOnlyThese=SoupStrainer('title'))
                    try:
                        titles = [title for title in SoupList]
                        title = pipobot.lib.utils.xhtml2text(titles[0].renderContents())
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
                    send.append("Je ne peux pas m'authentifier sur %s :'(" % url)
                elif error[1] == 404:
                    send.append("%s n'existe pas !" % url)
                elif error[1] == 403:
                    send.append("Il est interdit d'accéder à %s !" % url)
                else:
                    send.append("Erreur %s sur %s"%(error[1], url))
            except httplib.InvalidURL:
                send.append("L'URL %s n'est pas valide !" % url)
        return send
