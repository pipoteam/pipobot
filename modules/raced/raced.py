#! /usr/bin/python
# -*- coding: utf-8 -*-

from model import Racer
from pipobot.lib.modules import SyncModule, defaultcmd
import time
from sqlalchemy import func
from sqlalchemy.sql.expression import desc

class CmdRaced(SyncModule):
    """ Ajoute un point-raced à un collègue lent"""
    def __init__(self, bot):
        desc = "raced pseudo\nAjoute un point raced à /me envers pseudo"
        SyncModule.__init__(self, 
                            bot, 
                            desc = desc,
                            pm_allowed = False,
                            command = "raced",
                            )

    @defaultcmd
    def answer(self, sender, message):
        send = ''
        if message == '':
            return u"Donnez vous un point raced envers un ami ! écrivez !raced pseudo (10 s minimum d'intervalle)"
        sjid = self.bot.occupants.pseudo_to_jid(sender.strip())
        jid = self.bot.occupants.pseudo_to_jid(message)
        if jid == "":
            return u"%s n'est pas là..." % message

        if sjid == jid:
            return "Sans vouloir contrarier, ça va être dur là…"

        temps = int(time.time())
        res = self.bot.session.query(Racer).filter(Racer.jid_from == sjid).filter(Racer.jid_to == jid).all()

        if len(res) == 0:
            send = u"Félicitations %s, c'est la première fois que tu bats %s!" % (sender.strip(), message)
            r = Racer(sjid, jid, 1, temps)
            self.bot.session.add(r)
        else:
            racer = res[0]
            ecart = temps - int(racer.submission)
            if ecart>10:
                racer.score += 1
                date_bl = time.strftime("le %d/%m/%Y a %H:%M", time.localtime(float(racer.submission)))
                send = u"Nouveau score - %s : %d\n%d secondes depuis la dernière fois que tu as battu %s (%s)" % (sender.strip(), racer.score, ecart, message, date_bl)
                racer.submission = temps
        self.bot.session.commit()
        return send

    def cmd_score(self, sender, message):
        if message == []:
            return self.score_all(sender, message)
        elif message == ["total"]:
            return self.score_total(sender, message)

    def score_total(self, sender, message):
        sum_res = func.sum(Racer.score)
        classement = self.bot.session.query(Racer, sum_res).group_by(Racer.jid_from).order_by(desc(sum_res)).all()

        if len(classement) != 0:
            sc = "\nRaced - scores :\n"
            sc += " " + 60*"_"
            for racer in classement:
                if racer[1] != 0:
                    sc += "\n| "
                    pseudo_from = self.bot.occupants.jid_to_pseudo(racer[0].jid_from)
                    pseudo_to = self.bot.occupants.jid_to_pseudo(racer[0].jid_to)
    
                    if len(pseudo_from) > 30:
                        sc += "%s " % (pseudo_from[:30])
                    else:
                        sc += "%-30s " % (pseudo_from)
                    sc += "a raced au total %-3s fois " % (racer[1])
                    sc += " |"
            sc += "\n"
            sc +=  "|" + 59*"_" + "|"
            return {"text": sc, "monospace" : True}
        else:
            return "Aucun race, bande de nuls !"

    def score_all(self, sender, message):
        classement = self.bot.session.query(Racer).order_by(desc(Racer.score), Racer.jid_from).all()

        if len(classement) != 0:
            sc = "\nRaced - scores :\n"
            sc += " " + 82*"_"
            for racer in classement:
                sc += "\n| "
                pseudo_from = self.bot.occupants.jid_to_pseudo(racer.jid_from)
                pseudo_to = self.bot.occupants.jid_to_pseudo(racer.jid_to)

                if len(pseudo_from) > 30:
                    sc += "%s " % (pseudo_from[:30])
                else:
                    sc += "%-30s " % (pseudo_from)
                sc += "a battu %-3s fois " % (racer.score)

                if len(pseudo_to) > 30:
                    sc += "%s " % (pseudo_to[:30])
                else:
                    sc += "%-30s " % (pseudo_to)
                sc += " |"
            sc += "\n"
            sc +=  "|" + 81*"_" + "|"
            return {"text" : sc, "monospace" : True}
        else:
            return "Aucun race, bande de nuls !"

