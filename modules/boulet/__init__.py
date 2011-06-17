#! /usr/bin/python
# -*- coding: utf-8 -*-

import boulet
import scores


if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, boulet.CmdBoulet)
    register(__name__, scores.CmdScoresBoulet)
