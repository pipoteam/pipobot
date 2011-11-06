#! /usr/bin/python
# -*- coding: utf-8 -*-
from parser import extract,requete
from lib.modules import SyncModule, answercmd

class CmdTv(SyncModule):
    def __init__(self, bot):
        desc = "tv\nDonne les programmes tv de la soirée\n Les chaînes disponibles sont les suivantes :\n%s"%(", ".join(sorted(extract(requete.TNT).keys())))
        SyncModule.__init__(bot,
                                    desc = desc,
                                    command = "tv")
    
    #TODO split function using decorators
    @answercmd
    def answer(self, sender, message):
        args = message.strip()
        if args == "":
            channels = ["tf1", "france 2", "france 3", "canal+", "arte", "m6"]
            res = extract(requete.SOIREE)
            return "".join("%s : %s\n"%(key, res[key]) for key in channels)
        elif args == "channels":
            return "Les chaînes valides sont les suivantes :\n%s"%(", ".join(sorted(extract(requete.TNT).keys())))
        else:
            res = extract(requete.TNT)
            try:
                return "%s : %s"%(args, res[args.lower()])
            except KeyError:
                return "%s n'est pas une chaîne valide... Regardez le help pour plus d'informations"%(args)
