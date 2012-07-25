#! /usr/bin/python
# -*- coding: utf-8 -*-

from model import Blagueur
from pipobot.lib.modules import SyncModule, defaultcmd
import time

class AbstractBlague(SyncModule):
    """ Modifie les scores de blague """
    def __init__(self, bot, desc, command, autocongratulation, premier, operation):
        SyncModule.__init__(self,
                        bot,
                        desc = desc,
                        pm_allowed = False,
                        command = command,
                        )
        self.autocongratulation = autocongratulation
        self.premier = premier # S’utilise avec un %s pour le pseudo
        self.operation = operation
        self.init = self.operation(0, 1)

    @defaultcmd
    def answer(self, sender, message):
        send = ''
        if message == '':
            return self.desc
        sjid = self.bot.occupants.pseudo_to_jid(sender.strip())
        jid = self.bot.occupants.pseudo_to_jid(message)
        if jid == "":
            return "%s n'est pas dans le salon !" % message

        if sjid == jid:
            return self.autocongratulation

        temps = int(time.time())

        res = self.bot.session.query(Blagueur).filter_by(pseudo=jid).all()
        if len(res) == 0:
            b = Blagueur(jid, self.init, temps)
            self.bot.session.add(b)
            send = self.premier % message
        else:
            min_delay = 10
            blag = res[0]
            ecart = temps - blag.submission
            if ecart > min_delay:
                date_bl = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(blag.submission)))
                blag.score = self.operation(blag.score, 1)
                send =  u"Nouveau score - %s : %d\n%d secondes depuis ta dernière blague (%s)" % (message, blag.score, ecart, date_bl)
                blag.submission = temps
            else:
                send = "Ta dernière blague date de moins de %s secondes !"%(min_delay)
        self.bot.session.commit()
        return send
