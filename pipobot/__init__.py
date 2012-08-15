# -*- coding: utf-8 -*-

import fcntl
import logging
import os
import pwd
import signal
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from pipobot._version import __version__
from pipobot.config import get_configuration
from pipobot.lib.bdd import Base
from pipobot.lib.modules import BotModuleLoader
from pipobot.translation import setup_i18n
from pipobot.bot_jabber import BotJabber, XMPPException

LOGGER = logging.getLogger('pipobot.manager')


class PipoBotManager(object):
    """
    Object managing all bot instances.
    """

    __slots__ = ('_config', '_db_session', 'is_running')

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
        if self._config.daemonize:
            console_handler.setLevel(logging.WARNING)
        else:
            console_handler.setLevel(self._config.log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        try:
            file_handler = logging.FileHandler(self._config.logpath)
        except IOError as err:
            _abort("Unable to open the log file ‘%s’: %s",
                self._config.logpath, err.strerror)
        file_handler.setLevel(self._config.log_level)
        file_handler.setFormatter(formatter)
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
        if not self._config.pid_file :
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

    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGQUIT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)
        
        if self._config.daemonize:
            LOGGER.debug("Running in daemon mode")
            lock_fd = self._setup_lock_file()
        
        bots = []
        loader = BotModuleLoader(self._config.extra_modules,
            self._config.modules_conf)
        
        modules = {}
        for room in self._config.rooms:
            modules[room] = loader.get_modules(room.modules)
        self._configure_database()
        
        for room in self._config.rooms:
            try:
                bot = BotJabber(room.login, room.passwd, room.resource,
                    room.chan, room.nick, modules[room], self._db_session,  xmpp_log=None)
            except XMPPException, exc:
                LOGGER.error("Unable to join room '%s': %s", room.ident,
                    exc)
                continue
                
            bots.append(bot)
        
        if self._config.daemonize:
            lock_fh = self._daemonize(lock_fd)
        
        # For some reason, the xmpppy bots do not work correctly after a
        # fork(), so we only start them at this point
        for bot in bots:
            bot.start()

        del loader
        del self._config
        
        while self.is_running:
            signal.pause()
        
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        
        LOGGER.debug("Exiting…")
        for bot in bots:
            bot.kill()
        
        # Letting up to 1 second for the bots to finish
        for bot in bots:
            bot.join(1)

        logging.shutdown()

def _abort(message, *args):
    """
    Aborts the execution and prints a message on the console.
    """
    sys.stderr.write(message % args + "\n")
    sys.exit(1)
