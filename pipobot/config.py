# -*- coding: utf8 -*-

"""
Configuration parser module.
"""

from optparse import OptionParser, SUPPRESS_HELP
from os.path import basename
import logging
import sys
import yaml

from pipobot._version import __version__


def _abort(message, *args):
    """
    Aborts the execution and prints a message on the console.
    """
    sys.stderr.write(message % args + "\n")
    sys.exit(1)


class Configuration(object):
    """
    This class holds all settings used by the program.
    """

    __slots__ = ('log_level', 'daemonize', 'check_modules', 'pid_file',
                 'rooms', 'logpath', 'xmpp_logpath', 'database',
                 'lang', 'extra_modules', 'modules_conf')

    # Default values
    DEFAULT_CONF_FILE = "/etc/pipobot.conf.yml"
    DEFAULT_PIDFILE = ""

    def __init__(self, cmd_options, conf_file):
        self.log_level = cmd_options.log_level
        self.daemonize = cmd_options.daemonize
        self.check_modules = cmd_options.check_modules
        self.pid_file = cmd_options.pid_file
        self.rooms = []

        try:
            with open(conf_file) as f:
                data = yaml.load(f)
        except IOError, err:
            _abort("Unable to read the configuration file ‘%s’: %s.",
                   conf_file, err.strerror)
        except yaml.reader.ReaderError, err:
            _abort("The configuration file ‘%s’ seems incorrect or "
                   "corrupt: %s (position %s)", conf_file, err.reason,
                   err.position)
        except yaml.scanner.ScannerError, err:
            _abort("The configuration file seems incorrect or "
                   "corrupt: %s%s", err.problem, err.problem_mark)

        # Global configuration
        global_conf = data.get('config', {})
        for param in ['logpath', 'lang']:
            value = global_conf.get(param, "")
            if not value or not isinstance(value, basestring):
                _abort("Required parameter ‘%s’ not found or invalid in "
                       "configuration file ‘%s’.", param, conf_file)
            setattr(self, param, value)
        self.xmpp_logpath = global_conf.get('xmpp_logpath', None)

        self.extra_modules = global_conf.get('extra_modules', [])
        if isinstance(self.extra_modules, basestring):
            self.extra_modules = [self.extra_modules]
        elif type(self.extra_modules) != list:
            _abort("Parameter ‘extra_modules’ should be a string or a list in "
                   "configuration file ‘%s’.", conf_file)

        database = data.get("database", {})
        if type(database) != dict:
            _abort("Parameter ‘database’ should be a dictionary in "
                   "configuration file ‘%s’.", conf_file)

        if "engine" in database:
            if database["engine"] == "sqlite":
                if "src" in database:
                    self.database = "sqlite:///%s" % database["src"]
                else:
                    _abort("Parameter ‘src’ required for sqlite configuration in"
                           "file ‘%s’.", conf_file)
            elif database["engine"] == "mysql":
                try:
                    self.database = "mysql://%s:%s@%s/%s" % (database["user"], database["password"],
                                                             database["host"], database["name"])

                except KeyError as err:
                    _abort("Parameter ‘%s’ required for mysql configuration in"
                           "file ‘%s’.", err[0], conf_file)
            elif database["engine"] == "postgresql":
                try:
                    self.database = "postgresql://%s:%s@%s/%s" % (database["user"], database["password"],
                                                                  database["host"], database["name"])

                except KeyError as err:
                    _abort("Parameter ‘%s’ required for postgresql configuration in"
                           "file ‘%s’.", err[0], conf_file)
            else:
                _abort("Unknown database engine : %s", database["engine"])
        else:
            _abort("You need to specify a database engine !")

        # Module groups
        module_groups = {}
        groups_conf = data.get('groups', {})
        if type(groups_conf) != dict:
            _abort("Parameter ‘groups’ should be a dictionary in "
                   "configuration file ‘%s’.", conf_file)

        for group_name, group_items in groups_conf.iteritems():
            module_groups[group_name] = group = set()
            if type(group_items) != list:
                _abort("Parameter ‘groups[%s]’ should be a list in "
                       "configuration file ‘%s’.", group_name, conf_file)

            for group_item in group_items:
                if not isinstance(group_item, basestring):
                    _abort("Parameter ‘groups[%s]’ should only contain"
                           " strings in configuration file ‘%s’.", group_name,
                           conf_file)
                group.add(group_item)

        # Rooms
        self.rooms = []
        conf_rooms = data.get('rooms', [])
        if type(conf_rooms) != list:
            _abort("Parameter ‘rooms’ should be a dictionary in configuration "
                   "file ‘%s’.", conf_file)

        if not conf_rooms:
            _abort("No rooms are defined in configuration file ‘%s’.",
                   conf_file)

        for conf_room in conf_rooms:
            kwargs = {}
            for param in ['chan', 'login', 'passwd', 'resource', 'nick']:
                value = conf_room.get(param, "")
                if not value or not isinstance(value, basestring):
                    if "chan" in kwargs:
                        _abort("Required parameter ‘rooms[%s][%s]’ not found or "
                               "invalid in configuration file ‘%s’.", kwargs["chan"],
                               param, conf_file)
                    else:
                        _abort("One of your rooms needs a ‘chan‘ parameter")

                kwargs[param] = value

            kwargs['modules'] = modules = set()
            conf_modules = conf_room.get('modules')
            if conf_modules is None:
                conf_modules = []
            elif isinstance(conf_modules, basestring):
                conf_modules = [conf_modules]

            for conf_module in conf_modules:
                if not isinstance(conf_module, basestring):
                    _abort("Parameter ‘rooms[%s][modules]’ should only contain"
                           " strings in configuration file ‘%s’.", room_chan,
                           conf_file)

                if not conf_module or conf_module == "_":
                    continue

                if conf_module[0] == '_':
                    name = conf_module[1:]
                    if name not in module_groups:
                        _abort("Unknown module group ‘%s’ for room "
                               "configuration ‘%s’ in configuration file ‘%s’.",
                               name, room_chan, conf_file)

                    modules |= module_groups[name]

                else:
                    modules.add(conf_module)

            self.rooms.append(Room(**kwargs))

        # Module parameters
        modules_conf = data.get('modules_config')
        if modules_conf is None:
            modules_conf = {}

        self.modules_conf = modules_conf


class Room(object):
    __slots__ = ('chan', 'login', 'passwd', 'resource', 'nick', 'modules')

    def __init__(self, chan, login, passwd, resource, nick, modules):
        self.chan = chan
        self.login = login
        self.passwd = passwd
        self.resource = resource
        self.nick = nick
        self.modules = modules


def get_configuration():
    """
    Retrieve settings from the command line and the configuration file, and
    returns them in a Configuration object.
    """

    parser = OptionParser(version=__version__)
    if basename(sys.argv[0]).startswith('__main__'):
        parser.prog = "python -m pipobot"

    parser.set_defaults(log_level=logging.INFO, daemonize=False)
    parser.set_usage("Usage: %prog [options] [confpath]")

    parser.add_option("-q", "--quiet", action="store_const", dest="log_level",
                      const=logging.CRITICAL, help="Log and print only critical information")

    parser.add_option("-d", "--debug", action="store_const", dest="log_level",
                      const=logging.DEBUG, help="Log and print debug messages")

    parser.add_option("-b", "--background", action="store_const",
                      dest="daemonize", const=True,
                      help="Run in background, with reduced privileges")

    parser.add_option("-c", "--check-modules", action="store_const",
                      dest="check_modules", const=True, default=False,
                      help="Run in background, with reduced privileges")

    parser.add_option("--pid", dest="pid_file", type="string",
                      default=Configuration.DEFAULT_PIDFILE,
                      help="Specify a PID file (only used in background mode)")

    (options, args) = parser.parse_args()
    parser.destroy()

    conf_file = args[0] if len(args) > 0 else Configuration.DEFAULT_CONF_FILE

    return Configuration(options, conf_file)
