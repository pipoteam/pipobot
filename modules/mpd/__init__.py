#! /usr/bin/python2
# -*- coding: utf-8 -*-

import threading
from lib.BotMPD import BotMPD
from mpd import CommandError

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")
    

class CmdMpd(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.alive = True
        self.daemon = True
        self.verbose = False

        self.command = "mpd"
        self.bot = bot
        self.desc = """Controle du mpd
    mpd current : chanson actuelle
    mpd next/prev/play: c'est assez explicite
    mpd shuffle : fait un shuffle sur la playlist
    mpd list [n] : liste les [n] chansons suivantes
    mpd clear : vide la playlist (ou pas)
    mpd search (Artist|Title) requete : cherche toutes les pistes d'Artiste/Titre correspondant à la requête
    mpd setnext [i] : place la chanson à la position [i] dans la playlist après la chanson courante (enfin elle court pas vraiment)
    mpd nightmare [i] : les [i] prochaines chansons vont vous faire souffrir (plus que le reste)
    mpd clean : pour retarder l'inévitable...
    mpd connected : pour consulter le nombre de personnes connectées sur icecast
    mpd settag [artist|title]=Nouvelle valeur"""
        self.pm_allowed = False


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
        if cmd == "mute":
            if self.verbose:
                self.verbose = False
                send = "Bon d'accord je me la ferme mais venez pas bouder après !"
            else:
                send = "... Heu... c'est déjà le cas crétin..."
        elif cmd == "unmute":
            if self.verbose:
                send = "T'es aveugle ou quoi ? Je parle déjà !"
            else:
                self.verbose = True
                send = "C'est vrai je peux ? Vous allez SOUFFRIR !"
        elif cmds.has_key(cmd):
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

    def run(self):
        while self.alive:
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
                if r is not None and 'player' in r and self.verbose:
                    title = mpd.currentsongf()
                    self.bot.say("Nouvelle chanson : %s" % title)
                    for c in repDict:
                        if c in title:
                            self.bot.say(repDict[c])
                mpd.disconnect()
            except:
                continue
            

    def stop(self):
        self.alive = False

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdMpd(None)
    print o.answer('xouillet', 'nightmare 5') 
else:
    from .. import register
    register(__name__, CmdMpd)

