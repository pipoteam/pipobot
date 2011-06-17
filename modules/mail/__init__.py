#! /usr/bin/python
# -*- coding: utf-8 -*-

import threading
import traceback
import time
from email.header import decode_header
MAILFILE = '/var/mail/bot'

def decode_header_str(header):
    m = ''
    for head,enc in decode_header(header):
        if enc is None:
            m += head+' '
        else:
            m += head.decode(enc).encode("utf8")+' '
    return m

class AsyncMail(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.alive = True


        f = open(MAILFILE, "w")
        f.write('')
        f.close()
        self.file = open(MAILFILE) 

        self.command = 'mail'
        self.bot = bot

    def run(self):
        msubject = ""
        mfrom=""
        spam = -1
        while self.alive:
            t = self.file.readline()
            if t == '':
                time.sleep(1)
            if t[:5] == "From:":
                mfrom = decode_header_str(t[5:].strip())
            if t[:8] == "Subject:":
                msubject = decode_header_str(t[8:].strip())
            if t[:13] == "X-Spam-Score:":
                try:
                    spam = float(t[14:].strip())
                except:
                    spam = -2
            if mfrom != "" and msubject != "":
                if spam < 2:
                    try:
                        self.bot.say(">> Mail de %s : %s (Spam Score : %f)" % (mfrom, msubject, spam))
                    except:
                        self.bot.say(">> Mail de %s : <encodage foireux> (Spam Score : %f)" % (mfrom, spam))
                mfrom = ""
                msubject = ""
                spam = -1

    def stop(self):
        self.alive = False

if __name__ == '__main__':
    #Placer ici les tests unitaires
    t = AsyncMail(None)
    t.start()
    pass
else:
    from .. import register
    register(__name__, AsyncMail)

