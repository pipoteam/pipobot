#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib
from pipobot.lib.modules import AsyncModule, SyncModule, answercmd


class AppURLopener(urllib.FancyURLopener):
    """ Redefines the user-agent used to retrieve HTML content """
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = ("Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+"
               "(KHTML, like Gecko) Safari/531.2+ Midori/0.2")


class FortuneModule(SyncModule):
    """A module designed for html-parsing functions"""
    __usable = False

    def __init__(self, bot, desc, command, url_random,
                 url_indexed, lock_time=2):
        SyncModule.__init__(self,
                            bot,
                            desc=desc,
                            command=command,
                            lock_time=lock_time,
                            )
        self.url_random = url_random
        self.url_indexed = url_indexed

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        """ Called with !function [some int]"""
        index = message.group("index")
        page = self.url_indexed % index
        return self.retrieve_data(page)

    @answercmd(r"^$")
    def answer_random(self, sender, message):
        """ Called with !function and returns a random quote"""
        page = self.url_random
        return self.retrieve_data(page)

    def retrieve_data(self, url):
        """ Download the content of the url and try to extract data from it"""
        try:
            opener = AppURLopener()
            page = opener.open(url)
            content = page.read()
            page.close()
            return self.extract_data(content)
        except IOError as error:
            if error[1] == 401:
                return u"Je ne peux pas m'authentifier sur %s :'(" % url
            elif error[1] == 404:
                return u"%s n'existe pas !" % url
            elif error[1] == 403:
                return u"Il est interdit d'accéder à %s !" % url
            else:
                return u"Erreur %s sur %s" % (error[1], url)

    def extract_data(self, html_content):
        """ This *MUST* be overriden : it is the function that will extract
            content from retrieved HTML pages """
        return _("You must override extract_data for %s !!!") % self.command


class NotifyModule(SyncModule, AsyncModule):
    """A NotifyModule is an AsyncModule that you can also
        control with synchronous commands"""
    __usable = False

    def __init__(self, bot, desc, command,
                 pm_allowed=True, lock_time=0, delay=0):
        AsyncModule.__init__(self, bot, command, desc, delay)
        SyncModule.__init__(self, bot, desc, command, pm_allowed, lock_time)
        self._mute = True

    @answercmd("mute")
    def mute(self, sender, message):
        """ Disables notifications """
        self._mute = True
        return _("Disabling notifications for command %s") % self.command

    @answercmd("unmute")
    def unmute(self, sender, message):
        """ Enables notifications """
        self._mute = False
        self.update(silent=True)
        return _("Enabling notifications for command %s") % self.command

    def action(self):
        """ What will the module do every [delay] second """
        if not self._mute:
            self.do_action()

    def update(self, silent=False):
        """ Updates the ressource that is polled each [delay] second """
        return _("Not implemented")

    def do_action(self) :
        raise NotImplementedError("Must be subclassed")
