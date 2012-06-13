#!/usr/bin/python
# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String
from pipobot.lib.bdd import Base

class Racer(Base):
    __tablename__ = "raced"
    jid_from = Column(String(250), primary_key = True)
    jid_to = Column(String(250), primary_key = True)
    score = Column(Integer)
    submission = Column(Integer)

    def __init__(self, jid_from, jid_to, score, submission):
        self.jid_from = jid_from
        self.jid_to = jid_to
        self.score = score
        self.submission = submission
