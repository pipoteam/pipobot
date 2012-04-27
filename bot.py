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
import lib.abstract_modules
import lib.modules
import bot_jabber

#Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from lib.bdd import Base


# DEFAULT Constants
DEFAULT_LOG = "/tmp/botjabber.log"
DEFAULT_XMPPLOG = None #default = no log of xmpp messages
DEFAULT_LANG = "en"
APP_NAME = "pipobot"
DEFAULT_FILENAME = os.path.join(os.path.dirname(globals()["__file__"]),'settings.yml')

class ConfigException(Exception):
    """ A general exception raised when the configuration file is not valid """

    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return self.desc


class bot_manager:
    """ This is a class to configure, create, restart, manage bots """
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.bots = {}
        self.db_session = None
        self.update_config()
        self.xmpp_log = self.settings["config"]["xmpplog"] if "config" in self.settings and "xmpplog" in self.settings["config"] else DEFAULT_XMPPLOG

    def init_bots(self):
        """ This method will initialize all bots thanks to self.settings and start them """
        if "rooms" not in self.settings:
            raise ConfigException("You must have a 'rooms' section in your configuration file")
        for room in self.settings["rooms"]:
            self.create_bot(room)
        try:
            while raw_input("") != "q":
                continue
        except KeyboardInterrupt:
            logger.info(_("Ctrl-c signal !"))
        for bot_room, bot in self.bots.iteritems():
            logger.info("Killing bot from %s" % bot_room)
            bot.kill()
        sys.exit()

    def update_config(self):
        """ Reads again the configuration file and update settings """
        with open(self.settings_file) as f:
            self.settings = yaml.load(f)

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

    def read_modules(self, room):
        """ With the content of the configuration file, reads the
            list of modules to load, import all commands defined in them,
            and returns a list with all commands """
        if "modules" not in room:
            raise ConfigException("The room %s has no modules configured in %s" % (room["chan"], self.settings_file))
        classes_salon = []
        module_path = {}
        for module_name in room["modules"]:
            if module_name.startswith('_') :
                try:
                    group = self.settings["groups"][module_name[1:]]
                except KeyError as e:
                    raise ConfigException("Your configuration file must have a 'groups' section with the group %s required by the room %s" %
                                                (module_name[1:], room["chan"]))

            else :
                group = [module_name]
            for module in group:
                try:
                    module_class = __import__(module)
                except ImportError as e:
                    raise ConfigException("The module %s selected for %s cannot be found" % (module, room["chan"]))
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
        """ Restart the bot that is currently present in the room `bot_room` after
            having reading the configuration file again """
        self.update_config()
        for room in self.settings["rooms"]:
            if room["chan"] == bot_room:
                try:
                    self.bots[bot_room].kill()
                except AttributeError:
                    pass
                self.create_bot(room)

    def create_bot(self, room):
        """ Create a bot.
            `room` : an excerpt of the yaml structure generated with the configuration file
        """
        try:
            bot = bot_jabber.bot_jabber(room["login"], room["passwd"], room["ressource"],
                                        room["chan"], room["nick"], self.xmpp_log, self)
        except KeyError as e:
            if "chan" in room:
                msg = _("Your room %s has no parameter %s in %s" % (room["chan"], str(e), self.settings_file))
            else:
                msg = _("One of your room has no 'chan' parameter in %s" % self.settings_file)
            raise ConfigException(msg)

        classes_room, module_path = self.read_modules(room)
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

    settings_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILENAME

    with open(settings_filename) as s:
        try:
            settings = yaml.load(s)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            raise ConfigException("The configuration file %s is not a valid yaml file" % settings_filename)

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
        logger.error("The language %s is not supported, using %s instead"%(lang, DEFAULT_LANG))
        try:
            current_l = gettext.translation(APP_NAME, local_path, languages=[DEFAULT_LANG])
            current_l.install()
        except IOError:
            logger.error("Error loading english translation")
            logger.error("You must generate translation files by using scripts present in the 'translation' directory")
            raise ConfigException("Error loading english translation")

    # Configuring database
    engine = ""
    src = ""
    if "database" in settings:
        try:
            engine = settings["database"]["engine"]
            src = settings["database"]["src"]
            manager.configure_db(engine, src)
        except KeyError as e:
            raise ConfigException(_("Your database section must contain parameters 'engine' and 'src'"))

    # Configuring path to find modules
    sys.path.insert(0, "modules/")
    if "config" in settings and "extra_modules" in settings["config"] :
        for module_path in settings["config"]["extra_modules"] :
            sys.path.insert(0, module_path)

    manager.init_bots()
