# -*- coding: utf-8 -*-

import fcntl
import logging
import os
import pwd
import signal
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from pipobot._version import __version__
from pipobot.config import get_configuration
from pipobot.lib.bdd import Base
from pipobot.lib.loader import BotModuleLoader
from pipobot.translation import setup_i18n
from pipobot.bot_jabber import BotJabber, XMPPException
from pipobot.lib.module_test import ModuleTest
from pipobot.bot_test import TestBot

LOGGER = logging.getLogger('pipobot.manager')


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
            #filter to select sleekxmpp logs
            sleek_filter = logging.Filter("sleekxmpp")
            try:
                sleek_handler = logging.FileHandler(self._config.xmpp_logpath)
                sleek_handler.addFilter(sleek_filter)
                root_logger.addHandler(sleek_handler)
            except IOError as err:
                _abort("Unable to open the XMPP log file ‘%s’: %s",
                       self._config.xmpp_logpath, err.strerror)

        #filter to select pipobot logs
        pipobot_filter = logging.Filter("pipobot")
        if self._config.daemonize:
            console_handler.setLevel(logging.WARNING)
        else:
            console_handler.setLevel(self._config.log_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(pipobot_filter)
        root_logger.addHandler(console_handler)

        try:
            file_handler = logging.FileHandler(self._config.logpath)
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
        except OSError, e:
            _abort(str(e))
        except IOError, e:
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

    def _jabber_bot(self, modules):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGQUIT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)

        if self._config.daemonize:
            LOGGER.debug("Running in daemon mode")
            lock_fd = self._setup_lock_file()
            lock_fh = self._daemonize(lock_fd)

        bots = []

        for room in self._config.rooms:
            if room.testing:
                continue
            try:
                bot = BotJabber(room.login, room.passwd, room.resource,
                                room.chan, room.nick, modules[room],
                                self._db_session, self._config.use_ipv6)
            except XMPPException, exc:
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

    def _load_modules(self, unit_test=False):
        loader = BotModuleLoader(self._config.extra_modules,
                                 self._config.modules_conf)

        test_mods = []
        if unit_test:
            room = self.get_test_room()
            test_mods, modules = loader.get_modules(room.modules,
                                                    unit_test=True)
        else:
            modules = {}
            for room in self._config.rooms:
                if self._config.check_modules:
                    LOGGER.info("Checking modules configuration for room %s" %
                                room.chan)
                _, modules[room] = loader.get_modules(room.modules,
                                                      self._config.check_modules)
        del loader
        return test_mods, modules

    def get_test_room(self):
        for room in self._config.rooms:
            if room.testing:
                return room
        _abort("You must define a chan with testing: True parameter")

    def run(self):
        test_mods, modules = self._load_modules(self._config.unit_test or
                                                self._config.script or
                                                self._config.interract)

        self._configure_database()

        if not self._config.check_modules:

            if self._config.unit_test:
                test_room = self.get_test_room()
                bot = TestBot(test_room.nick, test_room.login,
                              test_room.chan, modules, self._db_session)
                suite = unittest.TestSuite()
                for test in test_mods:
                    suite.addTests(ModuleTest.parametrize(test, bot=bot))
                unittest.TextTestRunner(verbosity=2).run(suite)

            elif self._config.script:
                test_room = self.get_test_room()
                bot = TestBot(test_room.nick, test_room.login,
                              test_room.chan, modules, self._db_session)
                for msg in self._config.script.split(";"):
                    print "--> %s" % msg
                    print "<== %s" % bot.create_msg("bob", msg)
            elif self._config.interract:
                # We import it here so the bot does not 'depend' on twisted
                # unless you *really* want to use the --interract mode
                from pipobot.bot_twisted import TwistedBot
                test_room = self.get_test_room()
                bot = TwistedBot(test_room.nick, test_room.login,
                                 test_room.chan, modules, self._db_session)
            else:
                self._jabber_bot(modules)

        LOGGER.debug("Exiting…")
        logging.shutdown()
        del self._config


def _abort(message, *args):
    """
    Aborts the execution and prints a message on the console.
    """
    sys.stderr.write(message % args + "\n")
    sys.exit(1)
