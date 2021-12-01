# -*- coding: utf-8 -*-

import fcntl
import logging
import logging.handlers
import os
import signal
import sys
import errno
from queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from pipobot.config import get_configuration
from pipobot.lib.bdd import Base
from pipobot.lib.loader import BotModuleLoader
from pipobot.translation import setup_i18n
from pipobot.bot_jabber import BotJabber, XMPPException
from pipobot.bot_test import TestBot

LOGGER = logging.getLogger('pipobot.manager')

def console(bot):
    """
    Opens a python interpretor with the bot loaded.
    The bot itself can be retrieved with the local variable `bot`
    Each module can be retrieve with _module_name.
    Loaded modules are the one defined in the `test` section of the configuration.
    Example:
    in yaml configuration:

    test:
        fake_nick: Pipotest
        fake_chan: fake@example.org
        modules:
            - chiffres_lettres

    >>> from pprint import pprint
    >>> _chiffres.init("bob")
    'Nouvelle partie lancée\nTotal à trouver : 336\nNombres fournis : 5, 7, 10, 75, 75, 100'
    >>> pprint(_chiffres.solve("bob"))
    "J'ai trouvé une solution exacte : \n"
    '75 - 7 = 68\n'
    '68 + 100 = 168\n'
    '10 ÷ 5 = 2\n'
    '168 × 2 = 336'

    """

    import code
    import readline
    import rlcompleter

    list_modules = []
    loc = locals()
    for mod in bot.modules:
        local_name = "_" + mod.name
        loc[local_name] = mod
        list_modules.append(local_name)

    loc["bot"] = bot
    banner = ("Your bot is now loaded as `bot`\n"
              "Your instanciated modules can be accessed with `_module_name`\n"
              "Here is the list of the modules currently loaded :\n"
              "\t %s\n"
              "Now you are on your own, have fun !" % ", ".join(list_modules))
    vars = globals()
    vars.update(loc)
    readline.set_completer(rlcompleter.Completer(vars).complete)
    readline.parse_and_bind("tab: complete")
    shell = code.InteractiveConsole(vars)
    shell.interact(banner)


class PipoBotManager(object):
    """
    Object managing all bot instances.
    """

    __slots__ = ('_config', '_db_session', 'is_running', 'test_room')

    def __init__(self):
        self.is_running = True
        self._config = get_configuration()

        self._configure_logging()
        setup_i18n(self._config.lang)

    def _configure_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self._config.log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        # If we want to log XMPP debug
        if self._config.xmpp_logpath is not None:
            # filter to select sleekxmpp logs
            sleek_filter = logging.Filter("sleekxmpp")
            try:
                sleek_handler = logging.handlers.WatchedFileHandler(self._config.xmpp_logpath)
                sleek_handler.addFilter(sleek_filter)
                root_logger.addHandler(sleek_handler)
            except IOError as err:
                _abort("Unable to open the XMPP log file ‘%s’: %s",
                       self._config.xmpp_logpath, err.strerror)

        # filter to select pipobot logs
        pipobot_filter = logging.Filter("pipobot")
        if self._config.daemonize:
            console_handler.setLevel(logging.WARNING)
        else:
            console_handler.setLevel(self._config.log_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(pipobot_filter)
        root_logger.addHandler(console_handler)

        try:
            file_handler = logging.handlers.WatchedFileHandler(self._config.logpath)
        except IOError as err:
            _abort("Unable to open the log file ‘%s’: %s",
                   self._config.logpath, err.strerror)
        file_handler.setLevel(self._config.log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(pipobot_filter)
        root_logger.addHandler(file_handler)

    def _configure_database(self):
        kwargs = {}
        if self._config.database.startswith('mysql'):
            kwargs['pool_recycle'] = 3600

        engine = create_engine(self._config.database, convert_unicode=True,
                               **kwargs)
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.create_all(bind=engine)
        self._db_session = db_session

    def _signal_handler(self, signum, _):
        self.is_running = False

    def _setup_lock_file(self):
        if not self._config.pid_file:
            return

        try:
            fd = os.open(self._config.pid_file, os.O_WRONLY | os.O_CREAT)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            _abort(str(e))
        except IOError as e:
            if e.errno == errno.EACCES or e.errno == errno.EAGAIN:
                _abort("Unable to lock the PID file, is the bot already "
                       "running?")
            else:
                _abort(str(e))

        return fd

    def _daemonize(self, fd):
        pid = os.fork()

        if pid != 0:
            if fd is not None:
                os.ftruncate(fd, 0)
                os.write(fd, str(pid))
            os._exit(0)

        null = open(os.path.devnull)
        for desc in ['stdin', 'stdout', 'stderr']:
            getattr(sys, desc).close()
            setattr(sys, desc, null)

    def _jabber_bot(self, rooms, modules):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGQUIT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)

        if self._config.daemonize:
            LOGGER.debug("Running in daemon mode")
            lock_fd = self._setup_lock_file()
            lock_fh = self._daemonize(lock_fd)

        bots = []

        for room in rooms:
            try:
                bot = BotJabber(room.login, room.passwd, room.resource,
                                room.chan, room.nick, modules[room],
                                self._db_session, self._config.force_ipv4,
                                room.address, room.port)
            except XMPPException as exc:
                LOGGER.error("Unable to join room '%s': %s", room.chan,
                             exc)
                continue

            bots.append(bot)


        while self.is_running:
            signal.pause()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGHUP, signal.SIG_DFL)

        for bot in bots:
            bot.kill()

    def _load_modules(self, rooms) :
        loader = BotModuleLoader(self._config.modules_path,
                                 self._config.modules_conf)
        modules = {}
        errors  = 0
        for room in rooms:
            e, modules[room] = loader.get_modules(room.modules)
            errors += e
        del loader

        self._configure_database()

        return errors, modules

    def run(self):

        #
        # The different types of execution
        #

        # Only check modules: exit right after loading
        if self._config.only_check:
            self._load_modules(self._config.rooms)
            LOGGER.info("All modules checked, exiting…")

        # Test mode : load test room
        elif self._config.script or \
             self._config.interract or self._config.info_modules or self._config.console:
            
            test_room = self._config.test_room
            if test_room is None :
                _abort("Please define a test section in the configuration")
            e, m = self._load_modules([test_room])
            if e :
                _abort("Unable to load all test modules")

            # Script mode
            if self._config.script:
                bot = TestBot(test_room.nick, test_room.login,
                              test_room.chan, m[test_room],
                              self._db_session, output=Queue())
                for msg in self._config.script.split(";"):
                    print("--> %s" % msg)
                    ret = bot.create_msg("bob", msg)
                    ret.join()
                    print("<== %s" % bot.output.get())
                    bot.stop_modules()
            # Module info mode
            elif self._config.info_modules:
                bot = TestBot(test_room.nick, test_room.login,
                              test_room.chan, m[test_room].modules, self._db_session)
                from info_modules import info_modules
                info_modules(bot, self._config.modules_path)

            # Interract/twisted mode
            elif self._config.interract:
                # We import it here so the bot does not 'depend' on asyncio
                # unless you *really* want to use the --interract mode
                import asyncio
                from pipobot.bot_asyncio import AsyncioBot
                bot = AsyncioBot(test_room.nick, test_room.login,
                                 test_room.chan, m[test_room], self._db_session)
                loop = asyncio.get_event_loop()
                # TODO add this in the config file
                port = 4242
                f = asyncio.start_server(bot.accept_client, host=None, port=port)
                LOGGER.info("Bot started on port %d" % port)
                LOGGER.info("Connect to it with `telnet localhost %d`" % port)
                loop.run_until_complete(f)
                try:
                    loop.run_forever()
                except:
                    loop.stop()


            # Console mode
            elif self._config.console:
                bot = TestBot(test_room.nick, test_room.login,
                              test_room.chan, m[test_room], self._db_session)
                console(bot)

        # Standard mode
        else:
            rooms = self._config.rooms
            e, m = self._load_modules(rooms)
            if e :
                _abort("Unable to load all modules")

            self._jabber_bot(rooms, m)

        LOGGER.debug("Exiting…")
        logging.shutdown()
        del self._config


def _abort(message, *args):
    """
    Aborts the execution and prints a message on the console.
    """
    sys.stderr.write(message % args + "\n")
    sys.exit(1)
