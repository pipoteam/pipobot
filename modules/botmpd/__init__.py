#! /usr/bin/python2
# -*- coding: utf-8 -*-

from mpd import CommandError
from lib.modules import defaultcmd
from lib.abstract_modules import NotifyModule
from libmpd.BotMPD import BotMPD

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")

class CmdMpd(NotifyModule):
    def __init__(self, bot):
        desc = {"" : "Controle du mpd",
                "current" : "mpd current : chanson actuelle",
                "next" : "mpd next : chanson suivante",
                "prev" : "mpd prev : chanson précédente",
                "shuffle" : "mpd shuffle : fait un shuffle sur la playlist",
                "list" : "mpd list [n] : liste les [n] chansons suivantes",
                "clear" : "mpd clear : vide la playlist (ou pas)",
                "search" : "mpd search (Artist|Title) requete : cherche toutes les pistes d'Artiste/Titre correspondant à la requête",
                "setnext" : "mpd setnext [i] : place la chanson à la position [i] dans la playlist après la chanson courante (enfin elle court pas vraiment)",
                "nightmare" : "mpd nightmare [i] : les [i] prochaines chansons vont vous faire souffrir (plus que le reste)",
                "clean" : "mpd clean : pour retarder l'inévitable...",
                "connected" : "mpd connected : pour voir qui écoute le mpd",
                "settag" : "mpd settag [artist|title]=Nouvelle valeur",
                }
        NotifyModule.__init__(self,
                             bot,
                             desc = desc,
                             pm_allowed = False,
                             command = "mpd",
                             delay = 0)
        self.mute = True

    #TODO passer les commandes de lib/ ici et utiliser les décorateurs
    @defaultcmd
    def answer(self, sender, message):
        if hasattr(config, "DATADIR"):
            mpd = BotMPD(config.HOST, config.PORT, config.PASSWORD, config.DATADIR)
        else:
            mpd = BotMPD(config.HOST, config.PORT, config.PASSWORD)
        try:
            cmd, arg = message.split(' ', 1)
        except:
            cmd = message
            arg = ''

        # Table de correspondance entrée <-> méthode de BotMPD
        cmds = {'current': 'current',
                'next': 'next',
                'search': 'search',
                'prev': 'previous',
                'play': 'play',
#                'stop': 'stop',
#                'pause': 'pause',
                'list': 'nextplaylist',
                'settag': 'settag',
                'shuffle': 'shuffle',
                'setnext': 'setnext',
                'nightmare': 'nightmare',
                'clean': 'clean',
                'goto': 'goto',
                'coffee': 'coffee',
                'wakeup': 'wakeup',
                'connected': 'connected',
               }
        if cmds.has_key(cmd):
            try:
                if arg == '':
                    send = getattr(mpd, cmds[cmd])()
                else:
                    send = getattr(mpd, cmds[cmd])(arg)
            except (TypeError, CommandError):
                send = getattr(mpd, cmds[cmd])()
        else:
            send = "N'existe pas ça, RTFM. Ou alors tu sais pas écrire ..."

        mpd.disconnect()
        return send

    def action(self):
        # Here we redefine action (and not do_action as we are supposed to)
        # This is due to the fact that the "async" part here is handled by the idle()
        # function of the mpd library and not by a loop with sleep(delay) as usual
        try:
            mpd = BotMPD(config.HOST, config.PORT, config.PASSWORD)
            mpd.send_idle()
            r = mpd.fetch_idle()
            repDict = {"The Who - Baba O`riley":"La musique des experts !!!",
                        "The Who - Won't Get Fooled Again":"La musique des experts !!!",
                        "Oledaf et Monsieur D - Le café":"Coffee time !",
                        "Popcorn":"Moi aussi j'aime bien le popcorn",
                        "popcorn":"Moi aussi j'aime bien le popcorn",
                        "Ping Pong":"IPQ charlie est mauvais en ping pong :p",
                        "Daddy DJ":"<xouillet> on écoutait ca comme des dingues à La Souterraine en Creuse \o/ </xouillet>",
                        "Goldman":"JJG !!!",
#                            "Clapton":"<xouillet> owi c'est Joe !!! </xouillet>",
                        "Les 4 barbus - La pince a linge":"LA PINCE A LINGE !!!"}
            repDict["Les 4 barbus - La pince a linge"] = """
|\    /|
| \  / |
|  \/  |
|  ()  |
|_/||  |
|  ()  |
| (  ) |
|  ()  |
|  ||  |
|__/\__| """
            if r is not None and 'player' in r and not self.mute:
                title = mpd.currentsongf()
                self.bot.say("Nouvelle chanson : %s" % title)
                for c in repDict:
                    if c in title:
                        self.bot.say(repDict[c])
            mpd.disconnect()
        except:
            pass
        
