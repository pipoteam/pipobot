#! /usr/bin/python2
# -*- coding: utf-8 -*-
import time
import sqlite3
from consts import DB
from lib.bddtodo import BddTodo

class CmdTodo:
    """ Gestion de TODO-lists """
    def __init__(self, bot):
        self.command = "todo"
        self.bot = bot
        self.desc = """
    todo list : affiche la liste des todolist existantes.
    todo list [name] : affiche la liste des todo de la liste [name]
    todo add [name] [msg] : crée le nouveau todo [msg] dans la liste [name]
    todo remove [n,...] : supprime les todos d'id [n,...]
    todo search [element]: recherche un TODO qui contient [element]
    """
        self.pm_allowed = True

    def answer(self, sender, message):
        send = ''
        if message == '':
            return self.desc
        # Connection db
        bdd = BddTodo(DB)
        try:
            bdd.cursor.execute("SELECT * FROM todo")
        except:
            bdd.createtable()
        args = message.split(" ")
        name = args[0]
        try:
            send = getattr(self, name)(args[1:], bdd, sender)
        except AttributeError:
            send = "La commande %s n'existe pas pour !todo"%(name)
        return send

    def list(self, args, bdd, sender):
        if len(args) == 0:
            tmp = bdd.getlsts()
            if tmp == "":
                return "Pas de todolist…"
            else:
                return "Toutes les TODO-lists: \n%s"%(tmp)
        elif len(args) == 1:
            liste = args[0]
            if liste == "all":
                send = bdd.getalltodo()
            else:
                send = bdd.gettodo(liste)
            if send == "":
                return "TODO-list vide"
            return send
        else:
           return "usage: !todo list ou !todo list [une_liste]"
    
    def add(self, args, bdd, sender):
        if len(args) < 3:
            return "usage: !todo add [une_liste] [un_todo]"
        liste = args[0]
        if liste == "all":
            return "On ne peut pas nommer une liste 'all'"
        msg = " ".join(args[1:])
        bdd.newtodo(liste, msg, sender)
        return "TODO ajouté"

    def search(self, args, bdd, sender):
        if len(args) < 1:
            return "usage: !todo search [champ]"
        else:
            tosearch = " ".join(args)
            return bdd.search(tosearch)

    def remove(self, args, bdd, sender):
        send = ""
        if len(args) < 1:
            return "usage !todo remove id1,id2,id3,…"
        for i in args[0].split(","):
            n = int(i)
            deleted = bdd.deltodo(n)
            if deleted != "":
                send += "%s a été supprimé\n"%(deleted)
            else:
                send += "%s n'est pas dans la table"%(n)
        return send

if __name__ == "__main__":
    b = CmdTodo(None)
#    print b.answer("pipo", "todo list")
#    print b.answer("pipo", "todo add maliste un bo message")
#    print b.answer("pipo", "todo list maliste")
#    print b.answer("pipo", "todo delete 20")
    print b.answer("pipo", "todo search etbim")
