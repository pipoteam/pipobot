#! /usr/bin/python2
# -*- coding: utf-8 -*-
import time
import sqlite3
from consts import DB

class BddReminder:
    def __init__(self, file):    
        self.connection = sqlite3.connect(file)
        self.cursor = self.connection.cursor()
        self.createtable()

    def createtable(self):
        try:
            self.cursor.execute('CREATE TABLE reminder (id INTEGER PRIMARY KEY, owner string, description string, date INT, reporter string)')
            self.save()
        except sqlite3.OperationalError:
            pass #Table existe déjà

    def save(self):
        self.connection.commit()

    def lstreminds(self):
        res = self.cursor.execute("SELECT id,owner,description,date,reporter FROM reminder ORDER BY date").fetchall()
        return res

    def getowners(self):
        res = self.cursor.execute("SELECT owner FROM reminder ORDER BY owner").fetchall()
        return res
        
    def getallreminds(self):
        res = self.cursor.execute("SELECT id,owner,description,date,reporter FROM reminder ORDER BY date").fetchall()
        return self.format(res)

    def format(self, res):
        targets = {}
        if len(res) == 0:
            return ""

        for elt in res:
            date = time.strftime("%d/%m/%y,%Hh%M", time.localtime(float(elt[3])))
            try:
                targets[elt[1]] += "\t%s.%s (le %s par %s)\n"%(elt[0], elt[2], date, elt[4])
            except KeyError:
                targets[elt[1]] = "\t%s.%s (le %s par %s)\n"%(elt[0], elt[2], date, elt[4])

        ret = "".join(["%s : %s"%(owner, lst) for owner, lst in targets.iteritems()])
        return ret[0:-1] if ret != "" else ret

    def getreminds(self, owner):
        lookfor = (owner,)
        res = self.cursor.execute("SELECT id,owner,description,date,reporter FROM reminder WHERE owner=? ORDER BY date", lookfor).fetchall()
        restr = "\n".join(["%s.%s (le %s par %s)"%(event[0], event[2], time.strftime("%d/%m/%y,%Hh%M", time.localtime(float(event[3]))), event[4]) for event in res])
        return restr

    def newevent(self, owner, description, date, reporter):
        toadd = (owner, description, date, reporter)
        if date < time.time():
            return -1
        else:
            self.cursor.execute("INSERT INTO reminder values(null,?,?,?,?)", toadd)
            self.save()
            return 0

    def delreminder(self, id):
        try:
            todel = (id,)
            event = self.cursor.execute("SELECT id,owner,description,date,reporter FROM reminder WHERE id=?", todel).fetchall()
            date = time.strftime("%d/%m/%y,%Hh%M", time.localtime(float(event[0][3])))
            res = "%s.%s (le %s par %s)"%(event[0][0], event[0][2], date, event[0][4])
            self.cursor.execute("DELETE FROM reminder WHERE id=?", todel)
            self.save()
            return res
        except:
            return ""
            

if __name__ == "__main__":
    b = BddReminder("/srv/jabber/reminder.db")
    b.createtable()
    b.newevent("seb", "un event de test", 12345, "seb")
    print b.getallreminds()
    b.delreminder(1)
    print b.getallreminds()

