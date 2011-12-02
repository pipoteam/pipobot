#!/usr/bin/python
# -*- coding: UTF-8 -*-
import gettext
import logging
import os
from optparse import OptionParser
import sys
import yaml

import lib.modules

def conf_parser():
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
    # Reading configuration file
    settings_filename = args[0] if args else default_filename
    s = open(settings_filename)
    settings = yaml.load(s)
    s.close()
    return settings_filename, settings


def conf_logging(level, settings, appli_name, default_log):
    # Configuring logging
    logger = logging.getLogger(appli_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_filename = settings["config"]["logpath"] if "config" in settings and "logpath" in settings["config"] else default_log
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return log_filename, logger

def language(settings, logger, appli_name, default_lang):
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
    return db_session

def read_modules(salon_config, settings):
    classes_salon = []
    for module_name in salon_config:
        if module_name.startswith('_') :
            group = settings["groups"][module_name[1:]]
        else :
            group = [module_name]

        for module in group:
            module_class =__import__(module)
            classes = [getattr(module_class, class_name) for class_name in dir(module_class)]
            #XXX Quick FIX → all these classes are subclasses of BotModule too…
            except_list = [lib.modules.SyncModule, lib.modules.AsyncModule, lib.modules.MultiSyncModule, lib.modules.BotModule, lib.modules.ListenModule]
            for classe in [c for c in classes if type(c) == type and issubclass(c, lib.modules.BotModule) and c not in except_list]:
                classes_salon.append(classe)
    classes_salon.append(lib.modules.Help)
    return classes_salon
