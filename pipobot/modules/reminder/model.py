#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pipobot.lib.bdd
import time
from sqlalchemy import Column, Integer, String

class Remind(pipobot.lib.bdd.Base):
    __tablename__ = "remind"
    id = Column(Integer, primary_key = True, autoincrement = True)
    owner = Column(String(250))
    description = Column(String(250))
    date = Column(Integer(250))
    reporter = Column(String(250))

    def __init__(self, owner, description, date, reporter):
        self.owner = owner
        self.description = description
        self.date = date
        self.reporter = reporter

    def __str__(self):
        d = time.strftime("%d/%m/%Y à %H:%M", time.localtime(float(self.date)))
        return "%s. %s (le %s par %s)" % (self.id, self.description, d, self.reporter) 
