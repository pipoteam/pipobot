#!/usr/bin/python
# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String
from modules.bdd import Base

class Blagueur(Base):
    __tablename__ = "blagues"
    pseudo = Column(String, primary_key = True)
    score = Column(Integer)
    submission = Column(Integer)

    def __init__(self, pseudo, score, submission):
        self.pseudo = pseudo
        self.score = score
        self.submission = submission
