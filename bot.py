#! /usr/bin/python2 -Wignore::DeprecationWarning
# -*- coding: utf-8 -*-
"""Main module of the bot"""

import bot_jabber
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import lib.modules
import lib.init_bot

if __name__ == '__main__':

    # Constants
    DEFAULT_LOG = "/tmp/botjabber.log"
    DEFAULT_XMPPLOG = None #default = no log of xmpp messages
    DEFAULT_LANG = "en"
    APP_NAME = "pipobot"
    DEFAULT_FILENAME = os.path.join(os.path.dirname(globals()["__file__"]),'settings.yml')

    #Parametring options
    parser = lib.init_bot.conf_parser()

    #Reading command-line options
    (options, args) = parser.parse_args()

    #Reading configuration file
    settings_filename, settings = lib.init_bot.read_yml(args, DEFAULT_FILENAME)

    #Configuring logging
    log_filename, logger = lib.init_bot.conf_logging(options.level, settings, APP_NAME, DEFAULT_LOG)
    xmpp_log = settings["config"]["xmpplog"] if "config" in settings and "xmpplog" in settings["config"] else DEFAULT_XMPPLOG


    logger.info("-- Starting pipobot --")
    logger.info("Reading configuration file : %s" % settings_filename)
    logger.info("Logging file : %s" % log_filename)

    #Configuring language of the application
    lib.init_bot.language(settings, logger, APP_NAME, DEFAULT_LANG)

    #Configuring database
    engine = ""
    src = ""
    if "database" in settings:
        engine = settings["database"]["engine"]
        src = settings["database"]["src"]

    #Configuring path to find modules
    sys.path.insert(0, "modules/")
    if "extra_modules" in settings["config"] :
        for module_path in settings["config"]["extra_modules"] :
            sys.path.insert(0, module_path)

    # Starting bots
    bots = []
    for salon in settings["rooms"] :
        bot = bot_jabber.bot_jabber(salon["login"], salon["passwd"], salon["ressource"], 
                                    salon["chan"], salon["nick"], xmpp_log)
        classes_salon, module_path = lib.init_bot.read_modules(salon["modules"], settings)
        if engine:
            #Configuring database
            db_session = lib.init_bot.configure_db(engine, src)
            bot.session = db_session

        bot.module_path = module_path
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
