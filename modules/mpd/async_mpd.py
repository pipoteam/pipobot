#! /usr/bin/python2
# -*- coding: utf-8 -*-

import threading
from mpd import CommandError
from libmpd.BotMPD import BotMPD
from libmpd.modules import AsyncModule

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")
    
class AsyncMpd(AsyncModule):
    def __init__(self, bot):
        desc = "Display changes on the mpd server !"
        AsyncModule.__init__(self, 
                             bot, 
                             name = "checkmpd",
                             delay = 5,
                             desc = desc)

    def action(self):
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
