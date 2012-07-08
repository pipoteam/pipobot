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

    __slots__ = ('log_level', 'daemonize', 'user', 'pid_file', 'rooms',
        'log_path', 'xmpp_log_path', 'database', 'lang', 'extra_modules')

    # Default values
    DEFAULT_CONF_FILE = "/etc/pipobot.conf.yml"
    DEFAULT_USER = "nobody"
    DEFAULT_PIDFILE="/var/run/pipobot.pid"

    def __init__(self, cmd_options, conf_file):
        self.log_level = cmd_options.log_level
        self.daemonize = cmd_options.daemonize
        self.user = cmd_options.user
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
        for param in ['log_path', 'database', 'lang']:
            value = data.get(param, "")
            if not value or not isinstance(value, basestring):
                _abort("Required parameter ‘%s’ not found or invalid in "
                    "configuration file ‘%s’.", param, conf_file)
            setattr(self, param, value)

        self.extra_modules = data.get('extra_modules', [])
        if isinstance(self.extra_modules, basestring):
            self.extra_modules = [self.extra_modules]
        elif type(self.extra_modules) != list:
            _abort("Parameter ‘extra_modules’ should be a string or a list in "
                    "configuration file ‘%s’.", conf_file)
        
        self.xmpp_log_path = data.get('xmpp_log_path', None)

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
        if type(conf_rooms) != dict:
            _abort("Parameter ‘rooms’ should be a dictionary in configuration "
                "file ‘%s’.", conf_file)

        if not conf_rooms:
            _abort("No rooms are defined in configuration file ‘%s’.",
                conf_file)

        for room_ident, conf_room in conf_rooms.iteritems():
            if type(conf_room) != dict:
                _abort("Parameter ‘rooms[%s]’ should be a dictionary in "
                    "configuration file ‘%s’.", room_ident, conf_file)

            kwargs = {'ident': room_ident}
            for param in ['login', 'passwd', 'resource', 'nick']:
                value = conf_room.get(param, "")
                if not value or not isinstance(value, basestring):
                    _abort("Required parameter ‘rooms[%s][%s]’ not found or "
                        "invalid in configuration file ‘%s’.", room_ident,
                        param, conf_file)

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
                        " strings in configuration file ‘%s’.", room_ident,
                        conf_file)

                if not conf_module or conf_module == "_":
                    continue

                if conf_module[0] == '_':
                    name = conf_module[1:]
                    if name not in module_groups:
                        _abort("Unknown module group ‘%s’ for room "
                            "configuration ‘%s’ in configuration file ‘%s’.",
                            name, room_ident, conf_file)

                    modules |= module_groups[name]

                else:
                    modules |= conf_module

            self.rooms.append(Room(**kwargs))


class Room(object):
    __slots__ = ('ident', 'login', 'passwd', 'resource', 'nick', 'modules')

    def __init__(self, ident, login, passwd, resource, nick, modules):
        self.ident = ident
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

    parser.add_option("-u", "--user", dest="user", type="string",
        default=Configuration.DEFAULT_USER,
        help="User used for privileges reduction")

    parser.add_option("--pid", dest="pid_file", type="string",
        default=Configuration.DEFAULT_PIDFILE,
        help="Specify a PID file (only used in background mode)")

    (options, args) = parser.parse_args()
    parser.destroy()

    conf_file = args[0] if len(args) > 0 else Configuration.DEFAULT_CONF_FILE

    return Configuration(options, conf_file)