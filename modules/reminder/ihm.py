#! /usr/bin/python2
# -*- coding: utf-8 -*-
import time
from consts import DB
from lib.bddremind import BddReminder
from lib.parsedates import parseall, ParseExcept

class CmdReminder:
    def __init__(self, bot):
        self.command = "remind"
        self.bot = bot
        self.desc = """Un module pour se souvenir de choses
    remind list : affiche les personnes qui ont des alertes prévues.
    remind list [name] : affiche la liste des alertes pour [name]
    remind list_all : affiche toutes les alertes
    remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date au format [01/01/01,01h01] décrite par [desc]
    remind delete/remove [n,...] : supprime les alertes d'id [n,...]
    """
        self.pm_allowed = True

    def answer(self, sender, message):
        send = ''
        if message == '':
            return self.desc

        # Connection db
        bdd = BddReminder(DB)
        try:
            bdd.cursor.execute("SELECT * FROM reminder")
        except:
            bdd.createtable()
        
        args = message.split(" ")
        name = args[0]
        try:
            send = getattr(self, name)(args[1:], bdd, sender)
        except AttributeError:
            send = "La commande %s n'existe pas pour !remind"%(name)
        except ParseExcept as e:
            return str(e)
        return send
    
    def list(self, args, bdd, sender):
        #!remind list
        if len(args) == 0:
            owners = bdd.getowners()
            owners = list(set([elt[0] for elt in owners]))
            if owners == "":
                send = "Rien de prévu..."
            else:
                owners = [owner.encode("utf-8") for owner in owners]
                send = "Touts les gens qui vont être avertis : "+" ".join(owners)
        elif args[0] == "all":
            send = (bdd.getallreminds())
            if send == "":
                send = "Aucun événement prévu"
        else:
            who = args[0]
            send = bdd.getreminds(who) 
            if send == "":
                send = "Rien pour %s"%(who)
        return send

    def add(self, args, bdd, sender):
        #!remind add [owner] [date] [desc] : crée une alerte pour [owner] à la date [date] décrite par [desc]
        if len(args) < 3:
            send = "usage !remind add [owner] [date] [description]"
        else:
            owner = args[0] 
            date = args[1]
            try:
                datestruct = parseall(date)
                date = time.mktime(datestruct)
            except ValueError:
                return "La date doit être au format %d/%m/%y,%Hh%M"
            msg = " ".join(args[2:])
            error = bdd.newevent(owner, msg, date, sender)
            if error == -1:
                send = "On n'ajoute pas un événement dans le passé !!!"
            else:
                send = "Event ajouté pour le %s"%(time.strftime("%d/%m/%y,%Hh%M", time.localtime(date)))
        return send

    def delete(self, args, bdd, sender):
        return self.remove(args, bdd, sender)

    def remove(self, args, bdd, sender):
        send = ""
        if len(args) < 1:
            send = "usage !remind remove id1,id2,id3"
        else:
            try:
                for i in args[0].split(","):
                    n = int(i)
                    deleted = bdd.delreminder(n)
                    send += "%s a été supprimé\n"%(deleted)
            except:
                send = "RTFM ! Non vraiment Benoît, c'est toi qui te chie dessus. (Et c'est pas propre)"
        return send

if __name__ == "__main__":
    b = CmdReminder(None)
    print "add"
    print b.answer("pipo", "remind add seb 22/04/11,20h07 un rappel pour voir")
    print "list seb"
    print b.answer("pipo", "remind list seb")
