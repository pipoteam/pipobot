# -*- coding: utf-8 -*-

import fcntl
import logging
import os
import pwd
import signal
import sys

from pipobot._version import __version__
from pipobot.config import get_configuration
from pipobot.translation import setup_i18n
from pipobot.xmpp_bot import XMPPBot, XMPPException
from pipobot.modules import BotModuleLoader

LOGGER = logging.getLogger('manager')


class PipoBotManager(object):
    """
    Object managing all bot instances.
    """

    __slots__ = ('_config', 'is_running')

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
            file_handler = logging.FileHandler(self._config.log_path)
        except IOError as err:
            _abort("Unable to open the log file ‘%s’: %s",
                self._config.log_path, err.strerror)
        file_handler.setLevel(self._config.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    def _signal_handler(self, signum, _):
        self.is_running = False

    def _setup_lock_file(self):
        if os.getuid() != 0:
            _abort("This program must be started as root to work in the "
                "background.")
    
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
        try:
            info = pwd.getpwnam(self._config.user)
        except KeyError:
            _abort("The user ‘%s’ does not exist!", self._config.user)
    
        os.setgid(info.pw_gid)
        os.setuid(info.pw_uid)
    
        pid = os.fork()
        if pid != 0:
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
        
        if self._config.daemonize:
            lock_fd = self._setup_lock_file()
        
        bots = []
        loader = BotModuleLoader(self._config.extra_modules)
        for room in self._config.rooms:
            modules = loader.get_modules(room.modules)
            try:
                bot = XMPPBot(room.login, room.passwd, room.resource,
                    room.ident, room.nick, modules, xmpp_log=None)
            except XMPPException, exc:
                LOGGER.error("Unable to join room '%s': %s", room.ident,
                    exc)
                continue
                
            bot.start()
            bots.append(bot)
        
        if self._config.daemonize:
            lock_fh = self._daemonize(lock_fd)
        
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
