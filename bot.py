#! /usr/bin/python2 -Wignore::DeprecationWarning
# -*- coding: utf-8 -*-

import bot_jabber
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
import os,yaml
from optparse import OptionParser

from modules import liste_classes

# Constantes
DEFAULT_LOG="/tmp/botjabber.log"

# Paramétrage des options
parser = OptionParser()
parser.set_defaults(level=logging.INFO)
parser.set_usage("usage: %prog [options] [confpath] ")
parser.add_option("-q", "--quiet",
                  action="store_const", dest="level", const=logging.CRITICAL,
                  help="N'affiche que les erreurs critiques dans la console")
parser.add_option("-d", "--debug",
                  action="store_const", dest="level", const=logging.DEBUG,
                  help="Affiche les debugs")


(options, args) = parser.parse_args()

# Lecture de la conf
settings_filename = args[0] if args else os.path.join(os.path.dirname(globals()["__file__"]),'settings.yml')
s = open(settings_filename)
settings = yaml.load(s)
s.close()

# Paramétrage du log
logger = logging.getLogger('pipobot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(options.level)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

log_filename = settings["config"]["logpath"] if "config" in settings and "logpath" in settings["config"] else DEFAULT_LOG
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Hello world !

logger.info("-- Démarage de pipobot --")
logger.info("Lecture du fichier de configuration : %s" % settings_filename)
logger.info("Ajout du log dans le fichier : %s" % log_filename)

# Démarrage des bots
bots=[]
for salon in settings["salons"] :
    bot = bot_jabber.bot_jabber(salon["login"], salon["passwd"], salon["ressource"], salon["chan"], salon["nick"])
    classes_salon = []
    for module_name in salon["modules"]+["help"] :
        if module_name.startswith('_') :
            group = ["modules.%s" % module for module in settings["groupes"][module_name[1:]]]
        else :
            group = ["modules.%s" % module_name]

        for module in group :
            __import__(module)
            for classe in liste_classes[module] :
                classes_salon.append(classe)
    bot.add_commands(classes_salon)
    bot.start()
    bots.append(bot)

#On attend gentiment
try :
    while raw_input("") != 'q' :
        continue
except KeyboardInterrupt :
    logger.info("Fermeture par ctrl-c")

logger.info("Tuage des bots")
for bot in bots :
    bot.kill()
sys.exit()
