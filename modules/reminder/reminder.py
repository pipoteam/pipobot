#! /usr/bin/python2
# -*- coding: utf-8 -*-

import time
from lib.modules import SyncModule, answercmd
from model import Remind
from lib.parsedates import parseall, ParseExcept

class CmdReminder(SyncModule):
    def __init__(self, bot):
        desc = {"" : "Un module pour se souvenir de choses",
                "list" : """ remind list [name] : affiche la liste des alertes pour [name]
remind list all : affiche toutes les alertes""",
                "add" : "remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date au format [01/01/01,01h01] décrite par [desc]",
                "remove" : "remind delete/remove [n,...] : supprime les alertes d'id [n,...] ",
                }
        SyncModule.__init__(self, bot,  
                                desc = desc,
                                command = "remind")

    @answercmd("list$")
    def list(self, sender, args):
        owners = self.bot.session.query(Remind).group_by(Remind.owner).order_by(Remind.owner).all()
        owners = [remind.owner for remind in owners]
        if owners == []:
            send = "Rien de prévu..."
        else:
            send = "Touts les gens qui vont être avertis : "+" ".join(owners)
        return send

    @answercmd("list (?P<who>\S+)")
    def list_someone(self, sender, args):
        who = args.group("who")
        if who == "all":
           res = self.bot.session.query(Remind).order_by(Remind.owner).all()
           error_msg = "Aucun remind dans la base"
        else:
            res = self.bot.session.query(Remind).filter(Remind.owner == who).all()
            error_msg = "Rien de prévu pour %s" % who
        send = "\n".join([str(elt) for elt in res]) if res != [] else error_msg
        return send
    
    @answercmd("add (?P<owner>\S+) (?P<date>\S+) (?P<desc>.*)")
    def add(self, sender, args):
        #!remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date [date] décrite par [desc]
        owner = args.group("owner")
        date = args.group("date")
        msg = args.group("desc")
        try:
            datestruct = parseall(date)
            date = time.mktime(datestruct)
            date -= date % 60
        except (ValueError, AttributeError):
            return "La date doit être au format %d/%m/%y,%Hh%M"
        if date < time.time():
            send = "On n'ajoute pas un événement dans le passé !!!"
        else:
            r = Remind(owner, msg, date, sender)
            self.bot.session.add(r)
            self.bot.session.commit()
            send = "Event ajouté pour le %s"%(time.strftime("%d/%m/%y,%Hh%M", time.localtime(date)))
        return send
    
    @answercmd("(remove|delete) (?P<ids>(\d+,?)+)")
    def remove(self, sender, args):
        send = ""
        for i in args.group("ids").split(","):
            n = int(i)
            deleted = self.bot.session.query(Remind).filter(Remind.id == n).all()
            if deleted == []:
                send += "Pas de remind d'id %s\n"%(n)
            else:
                self.bot.session.delete(deleted[0])
                send += "%s a été supprimé\n"%(deleted[0])
        self.bot.session.commit()
        return send[0:-1]
