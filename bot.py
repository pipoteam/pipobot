#! /usr/bin/python2 -Wignore::DeprecationWarning
# -*- coding: utf-8 -*-
"""Main module of the bot"""

import bot_jabber
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
import os, yaml
import gettext
from optparse import OptionParser
import lib.modules


# Constants
DEFAULT_LOG = "/tmp/botjabber.log"
DEFAULT_XMPPLOG = None #default = no log of xmpp messages
DEFAULT_LANG = "en"
APP_NAME = "pipobot"

# Parametering options
parser = OptionParser()
parser.set_defaults(level=logging.INFO)
parser.set_usage("usage: %prog [options] [confpath] ")
parser.add_option("-q", "--quiet",
                  action="store_const", dest="level", const=logging.CRITICAL,
                  help="Just print critical errors in the terminal")
parser.add_option("-d", "--debug",
                  action="store_const", dest="level", const=logging.DEBUG,
                  help="Print debugs")

#Reading command-line options
(options, args) = parser.parse_args()

# Reading configuration file
settings_filename = args[0] if args else os.path.join(os.path.dirname(globals()["__file__"]),'settings.yml')
s = open(settings_filename)
settings = yaml.load(s)
s.close()

# Configuring logging
logger = logging.getLogger(APP_NAME)
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

xmpp_log = settings["config"]["xmpplog"] if "config" in settings and "xmpplog" in settings["config"] else DEFAULT_XMPPLOG

engine = ""
src = ""
# Database 
if "database" in settings:
    engine = settings["database"]["engine"]
    src = settings["database"]["src"]

logger.info("-- Starting pipobot --")
logger.info("Reading configuration file : %s" % settings_filename)
logger.info("Logging file : %s" % log_filename)

# Configuring language
lang = settings["lang"] if "lang" in settings else DEFAULT_LANG
logger.info("Language in config file : %s"%(lang))
local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
local_path = os.path.join(local_path,"locale")
try:
    current_l = gettext.translation(APP_NAME, local_path, languages=[lang])
    current_l.install()
except IOError:
    logger.error("The language %s is not supported, using %s instead"%(lang, DEFAULT_LANG))
    try:
        current_l = gettext.translation(APP_NAME, local_path, languages=[DEFAULT_LANG])
        current_l.install()
    except IOError:
        logger.error("Error loading english translations : no translation will be used")
        raise


sys.path.insert(0,"modules/")
if "extra_modules" in settings["config"] :
    for module_path in settings["config"]["extra_modules"] :
        sys.path.insert(0,module_path)

# Starting bots
bots = []
for salon in settings["rooms"] :
    bot = bot_jabber.bot_jabber(salon["login"], salon["passwd"], salon["ressource"], salon["chan"], salon["nick"], xmpp_log)
    classes_salon = []
    for module_name in salon["modules"] :
        if module_name.startswith('_') :
            group = settings["groups"][module_name[1:]]
        else :
            group = [module_name]

        for module in group:
            module_class =__import__(module)
            logger.info(dir(module_class))
            classes = [getattr(module_class, class_name) for class_name in dir(module_class)]
            classes.append(lib.modules.Help)
            #XXX Quick FIX → all these classes are subclasses of BotModule too…
            except_list = [lib.modules.SyncModule, lib.modules.AsyncModule, lib.modules.MultiSyncModule, lib.modules.BotModule, lib.modules.ListenModule]
            for classe in [c for c in classes if type(c) == type and issubclass(c, lib.modules.BotModule) and c not in except_list]:
                classes_salon.append(classe)

    if engine:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        from lib.bdd import Base

        engine = create_engine('sqlite:///%s' % src, convert_unicode=True)
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.create_all(bind=engine)
        bot.session = db_session

    bot.add_commands(classes_salon)
    bot.start()
    bots.append(bot)

try :
    while raw_input("") != 'q' :
        continue
except KeyboardInterrupt :
    logger.info(_("Ctrl-c signal !"))

logger.info(_("Killing bots"))
for bot in bots :
    bot.kill()
sys.exit()
