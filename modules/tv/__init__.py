#! /usr/bin/python
# -*- coding: utf-8 -*-
from parser import extract,requete

class CmdTv:
    def __init__(self, bot):
        self.command = "tv"
        self.bot = bot
        self.desc = "tv\nDonne les programmes tv de la soirée\n Les chaînes disponibles sont les suivantes :\n%s"%(", ".join(sorted(extract(requete.TNT).keys())))
	self.pm_allowed = True

    def answer(self, sender, message):
        args = message.strip()
        if args == "":
            channels = ["tf1", "france 2", "france 3", "canal+", "arte", "m6"]
            res = extract(requete.SOIREE)
            return "\n".join("%s : %s"%(key, res[key]) for key in channels)
        elif args == "channels":
            return "Les chaînes valides sont les suivantes :\n%s"%(", ".join(sorted(extract(requete.TNT).keys())))
        else:
            res = extract(requete.TNT)
            try:
                return "%s : %s"%(args, res[args.lower()])
            except KeyError:
                return "%s n'est pas une chaîne valide... Regardez le help pour plus d'informations"%(args)

class FakeBot:
    def __init__(self):
        self.name = "bot"
if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdTv(FakeBot())
    print o.answer('xouillet', 'tv') 
    print o.answer('xouillet', 'tv LCP')    
else:
    from .. import register
    register(__name__, CmdTv)

