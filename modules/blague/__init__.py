#! /usr/bin/python
# -*- coding: utf-8 -*-

import blague
import scores


if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, blague.CmdBlague)
    register(__name__, scores.CmdScores)

