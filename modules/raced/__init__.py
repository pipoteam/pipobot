#! /usr/bin/python
# -*- coding: utf-8 -*-

DB = '/srv/jabber/raced.db'
import scores
import raced


if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, raced.CmdRaced)
    register(__name__, scores.CmdRacedScores)

