#! /usr/bin/python
# -*- coding: utf-8 -*-
from model import Blagueur
import time

class CmdBlague:
    """ Ajoute un point-blague à un collègue blagueur compétent """
    def __init__(self, bot):
        self.command = "blague"
        self.bot = bot
        self.desc = "blague [pseudo]\nAjoute un point blague à [pseudo]"
        self.pm_allowed = False

    def answer(self, sender, message):
        send = ''
        if message == '':
            return u"Donnez un point blague à un ami ! écrivez !blague pseudo (10 s minimum d'intervalle)"
        sjid = self.bot.pseudo2jid(sender.strip())
        try:
            jid = self.bot.pseudo2jid(message)
        except KeyError:
            return u"%s n'est pas là..." % message

        if sjid == jid:
            return "Un peu de modestie, merde"

        temps = int(time.time())

        res = self.bot.session.query(Blagueur).filter_by(pseudo=jid).all()
        if len(res) == 0:
            b = Blagueur(jid, 1, temps)
            self.bot.session.add(b)
            send = u"Félicitations %s, c'est ta première blague !" % message
        else:
            min_delay = 10
            blag = res[0]
            ecart = temps - blag.submission
            if ecart > min_delay:
                date_bl = time.strftime("le %d/%m/%Y à %H:%M", time.localtime(float(blag.submission)))
                send =  u"Nouveau score - %s : %d\n%d secondes depuis ta dernière blague (%s)" % (message, blag.score + 1, ecart, date_bl)
                blag.score += 1
                blag.submission = temps
            else:
                send = "Ta dernière blague date de plus de %s secondes !"%(min_delay)
        self.bot.session.commit()
        return send
