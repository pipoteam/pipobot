#! /usr/bin/python
# -*- coding: utf-8 -*-

from abstractblague import AbstractBlague
from pipobot.lib.modules import SyncModule
from model import Blagueur
import operator

class CmdBlame(AbstractBlague):
    """ Enlève un point-blague à un collègue blagueur incompétent """
    def __init__(self, bot):
        desc = u"Enlevez un point blague à un ami ! écrivez !blame pseudo (10 s minimum d'intervalle)"
        AbstractBlague.__init__(self,
                                bot,
                                desc = desc,
                                command = "blame",
                                autocongratulation = "Oui, c’est bien de reconnaitre ses erreurs. Mais tu ferais mieux de juste de taire ;)",
                                premier = u"Ah, ben bravo %s, tu commences fort…",
                                operation = operator.sub)
