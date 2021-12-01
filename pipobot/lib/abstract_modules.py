#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
from pipobot.lib.modules import AsyncModule, SyncModule, answercmd


class AppURLopener(urllib.request.FancyURLopener):
    """ Redefines the user-agent used to retrieve HTML content """
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = ("Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+"
               "(KHTML, like Gecko) Safari/531.2+ Midori/0.2")


class FortuneModule(SyncModule):
    """A module designed for html-parsing functions"""
    __usable = False

    def __init__(self, bot, desc, name, url_random,
                 url_indexed, lock_time=2):
        SyncModule.__init__(self,
                            bot,
                            desc=desc,
                            name=name,
                            lock_time=lock_time,
                            )
        self.url_random = url_random
        self.url_indexed = url_indexed

    @answercmd(r"(?P<index>\d+)")
    def answer_int(self, sender, index):
        """ Called with !function [some int]"""
        page = self.url_indexed % index
        return self.retrieve_data(page)

    @answercmd("")
    def answer_random(self, sender):
        """ Called with !function and returns a random quote"""
        page = self.url_random
        return self.retrieve_data(page)

    def retrieve_data(self, url, encoding="utf-8"):
        """ Download the content of the url and try to extract data from it"""
        opener = AppURLopener()
        page = opener.open(url)
        code = page.getcode()
        if code == 401:
            return "Je ne peux pas m'authentifier sur %s :'(" % url
        elif code == 404:
            return "%s n'existe pas !" % url
        elif code == 403:
            return "Il est interdit d'accéder à %s !" % url
        elif code == 200:
            content = page.read()
            page.close()
            return self.extract_data(content.decode(encoding))
        else:
            return "Erreur %s sur %s" % (code, url)

    def extract_data(self, html_content):
        """ This *MUST* be overriden : it is the function that will extract
            content from retrieved HTML pages """
        return _("You must override extract_data for %s !!!") % self.name


class NotifyModule(SyncModule, AsyncModule):
    """A NotifyModule is an AsyncModule that you can also
        control with synchronous commands"""
    __usable = False

    def __init__(self, bot, desc, name,
                 pm_allowed=True, lock_time=0, delay=0):
        AsyncModule.__init__(self, bot, name, desc, delay)
        SyncModule.__init__(self, bot, desc, name, pm_allowed, lock_time)
        self._mute = True

    @answercmd("mute")
    def mute(self, sender):
        """ Disables notifications """
        self._mute = True
        return _("Disabling notifications for command %s") % self.name

    @answercmd("unmute")
    def unmute(self, sender):
        """ Enables notifications """
        self._mute = False
        self.update(silent=True)
        return _("Enabling notifications for command %s") % self.name

    def action(self):
        """ What will the module do every [delay] second """
        if not self._mute:
            self.do_action()

    def update(self, silent=False):
        """ Updates the ressource that is polled each [delay] second """
        return _("Not implemented")

    def do_action(self) :
        raise NotImplementedError("Must be subclassed")
