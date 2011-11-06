#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from sqlalchemy import Column, Integer, String
from lib.bdd import Base

class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String)
    content = Column(String)
    reporter = Column(String)
    submission = Column(Integer)

    def __init__(self, name, content, reporter, submission):
        self.name = name
        self.content = content
        self.reporter = reporter
        self.submission = submission

    def __str__(self):
        return "%s - %s (par %s le %s)" % (self.id, self.content, self.reporter, time.strftime("%d/%m/%Y à %H:%M", time.localtime(float(self.submission))))
