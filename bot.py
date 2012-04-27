#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from optparse import OptionParser
import gettext
import logging
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import yaml

#Bot jabber imports
import lib.modules
import bot_jabber

#Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from lib.bdd import Base
import lib.abstract_modules


# DEFAULT Constants
DEFAULT_LOG = "/tmp/botjabber.log"
DEFAULT_XMPPLOG = None #default = no log of xmpp messages
DEFAULT_LANG = "en"
APP_NAME = "pipobot"
DEFAULT_FILENAME = os.path.join(os.path.dirname(globals()["__file__"]),'settings.yml')

class bot_manager:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.bots = {}
        self.db_session = None
        self.update_config()
        self.xmpp_log = self.settings["config"]["xmpplog"] if "config" in self.settings and "xmpplog" in self.settings["config"] else DEFAULT_XMPPLOG

    def init_bots(self):
        for room in self.settings["rooms"]:
            self.create_bot(room)
        try:
            while raw_input("") != "q":
                continue
        except KeyboardInterrupt:
            logger.info(_("Ctrl-c signal !"))
        for bot in self.bots.values():
            bot.kill()
        sys.exit()

    def update_config(self):
        with open(self.settings_file) as f:
            settings = yaml.load(f)
        self.settings = settings

    def configure_db(self, engine, src):
        """ Configure database for bots,
            Create the 'db_session' that modules will use to access to the db """
        engine = create_engine('sqlite:///%s' % src, convert_unicode=True)
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.create_all(bind=engine)
        self.db_session = db_session

    @staticmethod
    def read_modules(room):
        """ With the content of the configuration file, reads the
            list of modules to load, import all commands defined in them,
            and returns a list with all commands """
        classes_salon = []
        module_path = {}
        for module_name in room["modules"]:
            if module_name.startswith('_') :
                group = self.settings["groups"][module_name[1:]]
            else :
                group = [module_name]
            for module in group:
                module_class = __import__(module)
                path = module_class.__path__
                module_path[module] = path[0]

                classes = [getattr(module_class, class_name) for class_name in dir(module_class)]
                #XXX Quick FIX → all these classes are subclasses of BotModule too…
                except_list = [lib.modules.SyncModule, lib.modules.AsyncModule,
                               lib.modules.MultiSyncModule, lib.modules.BotModule, lib.modules.ListenModule,
                               lib.abstract_modules.FortuneModule, lib.abstract_modules.NotifyModule]
                for classe in [c for c in classes if type(c) == type and \
                                                     issubclass(c, lib.modules.BotModule) and  \
                                                     c not in except_list]:
                    classes_salon.append(classe)
        #Modules RecordUsers and Help are used by default (no need to add them to the configuration)
        classes_salon.append(lib.modules.RecordUsers)
        classes_salon.append(lib.modules.Help)
        return classes_salon, module_path

    def restart(self, bot_room):
        self.update_config()
        for room in self.settings["rooms"]:
            if room["chan"] == bot_room:
                try:
                    self.bots[bot_room].kill()
                except AttributeError:
                    pass
                self.create_bot(room)

    def create_bot(self, room):
        bot = bot_jabber.bot_jabber(room["login"], room["passwd"], room["ressource"],
                                    room["chan"], room["nick"], self.xmpp_log, self)

        classes_room, module_path = bot_manager.read_modules(room)
        if self.db_session is not None:
            #TODO use manager attribute for that
            bot.session = self.db_session

        bot.module_path = module_path
        bot.add_commands(classes_room)
        bot.start()
        self.bots[room["chan"]] = bot

if __name__ == "__main__":
    #Parametring options
    parser = OptionParser()
    parser.set_defaults(level=logging.INFO)
    parser.set_usage("usage: %prog [options] [confpath] ")
    parser.add_option("-q", "--quiet",
                      action="store_const", dest="level", const=logging.CRITICAL,
                      help="Just print critical errors in the terminal")
    parser.add_option("-d", "--debug",
                      action="store_const", dest="level", const=logging.DEBUG,
                      help="Print debugs")
    (options, args) = parser.parse_args()

    if len(sys.argv) > 0:
        settings_filename = sys.argv[1] if sys.argv else DEFAULT_FILENAME

    with open(settings_filename) as s:
        settings = yaml.load(s)

    #Creation of bot_manager
    manager = bot_manager(settings_filename)

    #Configuring logging
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(options.level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_filename = settings["config"]["logpath"] if "config" in settings and \
                                                    "logpath" in settings["config"] else DEFAULT_LOG
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    # Configuring language
    lang = settings["lang"] if "lang" in settings else DEFAULT_LANG
    logger.info("Language in config file : %s"%(lang))
    local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    local_path = os.path.join(local_path,"locale")
    try:
        current_l = gettext.translation(APP_NAME, local_path, languages=[lang])
        current_l.install()
    except IOError:
        logger.error("The language %s is not supported, using %s instead"%(lang, default_lang))
        try:
            current_l = gettext.translation(appli_name, local_path, languages=[default_lang])
            current_l.install()
        except IOError:
            logger.error("Error loading english translations : no translation will be used")
            raise

    # Configuring database
    engine = ""
    src = ""
    if "database" in settings:
        engine = settings["database"]["engine"]
        src = settings["database"]["src"]
        manager.configure_db(engine, src)

    # Configuring path to find modules
    sys.path.insert(0, "modules/")
    if "extra_modules" in settings["config"] :
        for module_path in settings["config"]["extra_modules"] :
            sys.path.insert(0, module_path)

    manager.init_bots()
