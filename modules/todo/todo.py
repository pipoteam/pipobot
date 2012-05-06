#! /usr/bin/python2
# -*- coding: utf-8 -*-
import time
from sqlalchemy.orm.exc import NoResultFound
from pipobot.lib.modules import SyncModule, answercmd
from model import Todo

class CmdTodo(SyncModule):
    """ Gestion de TODO-lists """
    def __init__(self, bot):
        desc = {"" : "Gestion des TODO-lists",
                "list": """todo list : affiche la liste des todolist existantes.
todo list [name] : affiche les todo de la liste [name]""",
                "add" : "todo add [name] [msg] : crée le nouveau todo [msg] dans la liste [name]",
                "remove" : "todo remove [n,...] : supprime les todos d'id [n,...]",
                "search" : "todo search [element]: recherche un TODO qui contient [element]",
                }
        SyncModule.__init__(self,   
                                bot, 
                                desc = desc,
                                command = "todo")

    @answercmd("list")
    def list(self, sender, args):
        if args == "":
            tmp = self.bot.session.query(Todo).group_by(Todo.name).all()
            if tmp == []:
                return "Pas de todolist…"
            else:
                return "Toutes les TODO-lists: \n%s"%("\n".join([todo.name for todo in tmp]))
        else:
            liste = args
            if liste == "all":
                tmp = self.bot.session.query(Todo).order_by(Todo.name).all()
                listname = ""
                send = "\n"
                for elt in tmp:
                    if elt.name != listname:
                        send += "%s: \n" % (elt.name)
                        listname = elt.name
                    send += "\t%s \n" % elt
            else:
                tmp = self.bot.session.query(Todo).filter(Todo.name == liste).all()
                if tmp == []:
                    send = ""
                else:
                    send = "%s :\n%s"%(liste, "\n".join(map(str, tmp)))
            if send.strip() == "":
                return "TODO-list vide"
            return send
    
    @answercmd("add (?P<list_name>\S+) (?P<desc>.*)")
    def add(self, sender, args):
        liste = args.group("list_name")
        msg = args.group("desc")
        if liste == "all":
            return "On ne peut pas nommer une liste 'all'"
        todo = Todo(liste, msg, sender, time.time()) 
        self.bot.session.add(todo)
        self.bot.session.commit()
        return "TODO ajouté"

    @answercmd("search (?P<query>.*)")
    def search(self, sender, args):
        query = args.group("query")
        found = self.bot.session.query(Todo).filter(Todo.content.like("%" + query + "%"))
        return "\n".join(map(str, found))

    @answercmd("(remove|delete) (?P<ids>(\d+,?)+)")
    def remove(self, sender, args):
        send = ""
        arg = args.group("ids").split(",")
        for i in arg:
            n = int(i)
            deleted = self.bot.session.query(Todo).filter(Todo.id == n).all()
            if deleted == []:
                send += "Pas de todo d'id %s\n"%(n)
            else:
                self.bot.session.delete(deleted[0])
                send += "%s a été supprimé\n"%(deleted[0])
        self.bot.session.commit()
        return send[0:-1]
