#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from optparse import OptionParser
import gettext
import logging
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import imp
import yaml

#Bot jabber imports
import pipobot.lib.abstract_modules
import pipobot.lib.modules
import pipobot.bot_jabber

#Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from pipobot.lib.bdd import Base
from pipobot.lib.exceptions import ConfigException


# DEFAULT Constants
DEFAULT_LOG = "/tmp/botjabber.log"
DEFAULT_XMPPLOG = None #default = no log of xmpp messages
DEFAULT_LANG = "en"
APP_NAME = "pipobot"
DEFAULT_FILENAME = '/etc/pipobot/settings.yml'

class BotManager:
    """ This is a class to configure, create, restart, manage bots """
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.bots = {}
        self.db_session = None
        self.update_config()
        self.xmpp_log = self.settings["config"]["xmpplog"] if "config" in self.settings and "xmpplog" in self.settings["config"] else DEFAULT_XMPPLOG

    def init_bots(self, modules_paths):
        """ This method will initialize all bots thanks to self.settings and start them """
        if "rooms" not in self.settings:
            raise ConfigException(_("You must have a 'rooms' section in your configuration file"))
        for room in self.settings["rooms"]:
            self.create_bot(room, modules_paths)
        try:
            while raw_input("") != "q":
                continue
        except KeyboardInterrupt:
            logger.info(_("Ctrl-c signal !"))
        for bot_room, bot in self.bots.iteritems():
            logger.info(_("Killing bot from %s" % bot_room))
            bot.kill()
        sys.exit()

    def update_config(self):
        """ Reads again the configuration file and update settings """
        with open(self.settings_file) as f:
            self.settings = yaml.load(f)

    def configure_db(self):
        """ Configure database for bots,
            Create the 'db_session' that modules will use to access to the db """
        engine = create_engine('%s:///%s' % (self.db_engine, self.db_src), convert_unicode=True)
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.create_all(bind=engine)
        self.db_session = db_session

    def read_modules(self, room, modules_paths):
        """ With the content of the configuration file, reads the
            list of modules to load, import all commands defined in them,
            and returns a list with all commands """
        if "modules" not in room:
            raise ConfigException(_("The room %s has no modules configured in %s") % (room["chan"], self.settings_file))
        classes_salon = []
        module_path = {}
        for module_name in room["modules"]:
            if module_name.startswith('_') :
                try:
                    group = self.settings["groups"][module_name[1:]]
                except KeyError as e:
                    raise ConfigException(_("Your configuration file must have a 'groups' section with the group %s required by the room %s") %
                                                (module_name[1:], room["chan"]))
            else :
                group = [module_name]
            for module in group:
                try:
                    infos = imp.find_module(module, modules_paths)
                    module_class = imp.load_module(module, *infos)
                except ImportError as e:
                    raise ConfigException(_("The module %s selected for %s cannot be loaded. Error was '%s'") % (module, room["chan"], str(e)))
                path = module_class.__path__
                module_path[module] = path[0]

                classes = [getattr(module_class, class_name) for class_name in dir(module_class)]
                for c in classes :
                    if type(c) == type and issubclass(c, pipobot.lib.modules.BotModule) and \
                        not hasattr(c, '_%s__usable' % c.__name__) :
                        classes_salon.append(c)
        #Modules RecordUsers and Help are used by default (no need to add them to the configuration)
        classes_salon.append(pipobot.lib.modules.RecordUsers)
        classes_salon.append(pipobot.lib.modules.Help)
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

    def create_bot(self, room, modules_paths):
        """ Create a bot.
            `room` : an excerpt of the yaml structure generated with the configuration file
        """
        try:
            bot = pipobot.bot_jabber.BotJabber(room["login"], room["passwd"],
                                               room["ressource"], room["chan"],
                                               room["nick"], self.xmpp_log, self)
            bot.settings = self.settings
        except KeyError as e:
            if "chan" in room:
                msg = _("Your room %s has no parameter %s in %s" % (room["chan"], str(e), self.settings_file))
            else:
                msg = _("One of your room has no 'chan' parameter in %s" % self.settings_file)
            raise ConfigException(msg)

        classes_room, module_path = self.read_modules(room, modules_paths)
        self.configure_db()
        if self.db_session is not None:
            #TODO use manager attribute for that
            bot.session = self.db_session

        bot.module_path = module_path
        bot.add_commands(classes_room)
        bot.start()
        self.bots[room["chan"]] = bot

def main():
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

    settings_filename = args[0] if len(args) > 0 else DEFAULT_FILENAME

    with open(settings_filename) as s:
        try:
            settings = yaml.load(s)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            raise ConfigException("The configuration file %s is not a valid yaml file" % settings_filename)

    #Creation of BotManager
    manager = BotManager(settings_filename)

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
            manager.db_engine = engine
            manager.db_src = src
        except KeyError as e:
            raise ConfigException(_("Your database section must contain parameters 'engine' and 'src'"))

    # Configuring path to find modules
    modules_paths = ["modules"]
    if "config" in settings and "extra_modules" in settings["config"] :
        modules_paths += settings["config"]["extra_modules"]

    manager.init_bots(modules_paths)

if __name__ == '__main__':
    main()
