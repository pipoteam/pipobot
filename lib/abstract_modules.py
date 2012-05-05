#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib
from BeautifulSoup import BeautifulSoup
from lib.modules import AsyncModule, SyncModule, defaultcmd, answercmd

class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"

class FortuneModule(SyncModule):
    def __init__(self, bot, desc, command, url_random, url_indexed, lock_time = 2):
        SyncModule.__init__(self,
                            bot,
                            desc = desc,
                            command = command,
                            lock_time = lock_time,
                            )
        self.url_random = url_random
        self.url_indexed = url_indexed

    @answercmd(r"(?P<index>\d+)$")
    def answer_int(self, sender, message):
        index = message.group("index")
        page = self.url_indexed % index
        return self.retrieve_data(page)

    @answercmd(r"^$")
    def answer_random(self, sender, message):
        page = self.url_random
        return self.retrieve_data(page)

    def retrieve_data(self, url):
        opener = AppURLopener()
        page = opener.open(url)
        contenu = page.read()
        page.close()
        soup = BeautifulSoup(contenu)
        return self.extract_data(soup)

    def extract_data(self, soup):
        return _("You must override extract_data for %s !!!") % self.command

class NotifyModule(SyncModule, AsyncModule):
    """A NotifyModule is an AsyncModule that you can also control with synchronous commands"""
    def __init__(self, bot, desc, command, pm_allowed=True, lock_time=0, delay=0):
        AsyncModule.__init__(self, bot, command, desc, delay, pm_allowed)
        SyncModule.__init__(self, bot, desc, command, pm_allowed, lock_time)
        self.mute = False

    @answercmd("mute")
    def mute(self, sender, message):
        self.mute = True
        return _("Disabling notifications for command %s") % self.command

    @answercmd("unmute")
    def unmute(self, sender, message):
        self.mute = False
        self.update(silent = True)
        return _("Enabling notifications for command %s")  % self.command

    def action(self):
        if not self.mute:
            self.do_action()

    def update(self, silent = False):
        return _("Not implemented")
