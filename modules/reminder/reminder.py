#! /usr/bin/python2
# -*- coding: utf-8 -*-

import time
from lib.modules import SyncModule, answercmd
from model import Remind
from parsedates import parseall, ParseExcept

class CmdReminder(SyncModule):
    def __init__(self, bot):
        desc = {"" : "Un module pour se souvenir de choses",
                "list" : """remind list : affiche les personnes qui ont des alertes prévues.
remind list [name] : affiche la liste des alertes pour [name]
remind list all : affiche toutes les alertes""",
                "add" : "remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date au format [01/01/01,01h01] décrite par [desc]",
                "remove" : "remind delete/remove [n,...] : supprime les alertes d'id [n,...] ",
                }
        SyncModule.__init__(self, bot,  
                                desc = desc,
                                command = "remind")

    @answercmd("list")
    def list(self, sender, args):
        #!remind list
        args = args.split()
        if args == []:
            owners = self.bot.session.query(Remind).group_by(Remind.owner).order_by(Remind.owner).all()
            owners = [remind.owner for remind in owners]
            if owners == []:
                send = "Rien de prévu..."
            else:
                send = "Touts les gens qui vont être avertis : "+" ".join(owners)
        elif args[0] == "all":
            reminds = self.bot.session.query(Remind).order_by(Remind.owner).all()
            #TODO add owner in output
            send = "\n".join([str(remind) for remind in reminds])
            if send == "":
                send = "Aucun événement prévu"
        else:
            who = args[0]
            res = self.bot.session.query(Remind).filter(Remind.owner == who).all()
            send = "\n".join([str(elt) for elt in res])
            if send == "":
                send = "Rien pour %s"%(who)
        return send
    
    @answercmd("add")
    def add(self, sender, args):
        #!remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date [date] décrite par [desc]
        try:
            owner, date, msg = args.split(" ", 2)
        except ValueError:
            return "usage !remind add [owner] [date] [description]"
        try:
            datestruct = parseall(date)
            date = time.mktime(datestruct)
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
    
    @answercmd("delete", "remove")
    def remove(self, sender, args):
        args = args.split()
        send = ""
        if len(args) < 1:
            send = "usage !remind remove id1,id2,id3"
        else:
            for i in args[0].split(","):
                n = int(i)
                deleted = self.bot.session.query(Remind).filter(Remind.id == n).all()
                if deleted == []:
                    send += "Pas de remind d'id %s\n"%(n)
                else:
                    self.bot.session.delete(deleted[0])
                    send += "%s a été supprimé\n"%(deleted[0])
        self.bot.session.commit()
        return send[0:-1]
