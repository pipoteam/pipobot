#! /usr/bin/python
# -*- coding: utf-8 -*-

import nextep
import prevep


if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, nextep.CmdNextep)
    register(__name__, prevep.CmdPrevep)

