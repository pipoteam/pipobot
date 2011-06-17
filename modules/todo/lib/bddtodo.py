#! /usr/bin/python2
# -*- coding: utf-8 -*-

import time
import sqlite3
from consts import DB

class BddTodo:
    def __init__(self, file):    
        self.connection = sqlite3.connect(file)
        self.cursor = self.connection.cursor()

    def createtable(self):
        try:
            self.cursor.execute('CREATE TABLE todo (id INTEGER PRIMARY KEY, name string, content string, reporter string)')
            self.save()
        except sqlite3.OperationalError:
            pass #Table existe déjà

    def save(self):
        self.connection.commit()

    def getalltodo(self):
        res = self.cursor.execute("SELECT id,content,reporter, name FROM todo ORDER BY name").fetchall()
        return self.format(res)

    def format(self, res):
        if res == []:
            return ""
        lastname = res[0][3]
        restr = "\n%s:\n"%lastname
        for todo in res:
            if todo[3] != lastname:
                restr += "%s:\n"%todo[3]
                lastname = todo[3]
            restr += "\t%s.%s (par %s)\n"%(todo[0], todo[1], todo[2])
        return restr[:-1]

    def gettodo(self, name):
        lookfor = (name,)
        res = self.cursor.execute("SELECT id,content,reporter FROM todo WHERE name=?", lookfor).fetchall()
        restr = ""
        for todo in res:
            restr += "%s.%s (par %s)\n"%(todo[0], todo[1], todo[2])
        return restr[:-1]

    def newtodo(self, name, content, reporter):
        toadd = (name, content, reporter)
        self.cursor.execute("INSERT INTO todo values(null,?,?,?)", toadd)
        self.save()

    def deltodo(self, id):
        try:
            todel = (id,)
            todo = self.cursor.execute("SELECT id,content,reporter FROM todo WHERE id=?", todel).fetchall()
            res = "%s.%s (par %s)"%(todo[0][0], todo[0][1], todo[0][2])
            self.cursor.execute("DELETE FROM todo WHERE id=?", todel)
            self.save()
            return res
        except:
            return ""
            
    def getlsts(self):
        req = self.cursor.execute("SELECT name FROM todo").fetchall()
        req = list(set(req))
        res = ""
        for elt in req:
            res += "%s\n"%(elt)
        return res

    def search(self, criteria):
        print criteria
        tosearch = ("%"+criteria+"%",)
        req1 = self.cursor.execute("SELECT id,content,reporter,name FROM todo WHERE content LIKE ?", tosearch).fetchall()
        req2 = self.cursor.execute("SELECT id,content,reporter,name FROM todo WHERE reporter LIKE ?", tosearch).fetchall()
        req1.extend(req2)
        return self.format(req1)


if __name__ == "__main__":
    b = BddTodo("/srv/jabber/todo.db")
    print b.getlsts()
#    b.createtable()
#    b.newtodo("pipolst", "un beau pipo", "seb")
#    print b.gettodo("pipolst")
#    b.deltodo(1)
#    print b.gettodo("pipolst")
#    print b.getlsts()
    print b.search("etbim")
