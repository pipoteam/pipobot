#!/usr/bin/python
# -*- coding: UTF-8 -*-
import gettext
import logging
import os
from optparse import OptionParser
import sys
import yaml

import lib.modules
import lib.abstract_modules

def conf_parser():
    """Reads command-line parameters used to start the bot"""
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
    return parser

def read_yml(args, default_filename):
    """Reads yml configuration file and returns its content"""
    settings_filename = args[0] if args else default_filename
    s = open(settings_filename)
    settings = yaml.load(s)
    s.close()
    return settings_filename, settings


def conf_logging(level, settings, appli_name, default_log):
    """Configuration of logging"""
    logger = logging.getLogger(appli_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_filename = settings["config"]["logpath"] if "config" in settings and \
                                                    "logpath" in settings["config"] else default_log
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return log_filename, logger

def language(settings, logger, appli_name, default_lang):
    """ Configure language of the bot """
    # Configuring language
    lang = settings["lang"] if "lang" in settings else default_lang
    logger.info("Language in config file : %s"%(lang))
    local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    local_path = os.path.join(local_path,"locale")
    try:
        current_l = gettext.translation(appli_name, local_path, languages=[lang])
        current_l.install()
    except IOError:
        logger.error("The language %s is not supported, using %s instead"%(lang, default_lang))
        try:
            current_l = gettext.translation(appli_name, local_path, languages=[default_lang])
            current_l.install()
        except IOError:
            logger.error("Error loading english translations : no translation will be used")
            raise

def configure_db(engine, src):
    """ Configure database for the application """
    if engine:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        from lib.bdd import Base

        engine = create_engine('sqlite:///%s' % src, convert_unicode=True)
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.create_all(bind=engine)
    return db_session

def read_modules(salon_config, settings):
    """ With the content of the configuration file, reads the 
        list of modules to load, import all commands defined in them, 
        and returns a list with all commands """
    classes_salon = []
    module_path = {}
    for module_name in salon_config:
        if module_name.startswith('_') :
            group = settings["groups"][module_name[1:]]
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
                           lib.abstract_modules.FortuneModule]
            for classe in [c for c in classes if type(c) == type and \
                                                 issubclass(c, lib.modules.BotModule) and  \
                                                 c not in except_list]:
                classes_salon.append(classe)
    #Modules RecordUsers and Help are used by default (no need to add them to the configuration)
    classes_salon.append(lib.modules.RecordUsers)
    classes_salon.append(lib.modules.Help)
    return classes_salon, module_path
