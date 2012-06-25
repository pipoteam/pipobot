#! /usr/bin/python
# -*- coding: utf-8 -*-

import threading
import traceback
import time
from email.header import decode_header
from pipobot.lib.modules import AsyncModule
MAILFILE = '/var/mail/bot'

def decode_header_str(header):
    m = ''
    for head,enc in decode_header(header):
        if enc is None:
            m += head+' '
        else:
            m += head.decode(enc).encode("utf8")+' '
    return m

class AsyncMail(AsyncModule):
    def __init__(self, bot):
        AsyncModule.__init__(self, 
                             bot,  
                             name = "mail",
                             desc = "Displaying incoming mails",
                             delay = 0)
        f = open(MAILFILE, "w")
        f.write('')
        f.close()

        self.file = open(MAILFILE) 
        self.msubject = ""
        self.mfrom=""
        self.spam = -1

    def action(self):
        t = self.file.readline()
        if t == '':
            time.sleep(1)
        if t[:5] == "From:":
            self.mfrom = decode_header_str(t[5:].strip())
        if t[:8] == "Subject:":
            self.msubject = decode_header_str(t[8:].strip())
        if t[:13] == "X-Spam-Score:":
            try:
                self.spam = float(t[14:].strip())
            except:
                self.spam = -2
        if self.mfrom != "" and self.msubject != "":
            if self.spam < 0:
                try:
                    self.bot.say(">> Mail de %s : %s (Spam Score : %f)" % (self.mfrom, self.msubject, self.spam))
                except:
                    self.bot.say(">> Mail de %s : <encodage foireux> (Spam Score : %f)" % (self.mfrom, self.spam))
            self.mfrom = ""
            self.msubject = ""
            self.spam = -1
