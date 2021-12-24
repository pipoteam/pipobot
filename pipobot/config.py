# -*- coding: utf-8 -*-

"""
Configuration parser module.
"""

from optparse import OptionParser
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


def _info(message, *args):
    """
    Prints a message on the console.
    """
    sys.stdout.write(message % args + "\n")


class Configuration(object):
    """
    This class holds all settings used by the program.
    """

    __slots__ = ('log_level', 'daemonize', 'only_check', 'pid_file',
                 'rooms', 'logpath', 'xmpp_logpath', 'database', 'lang',
                 'modules_path', 'modules_conf', 'unit_test', 'script',
                 'interract', 'console', 'force_ipv4', 'test_room', 'info_modules')


    # Default values
    DEFAULT_CONF_FILE = "/etc/pipobot.conf.yml"
    DEFAULT_PIDFILE = ""

    def __init__(self, cmd_options, conf_file):
        self.log_level = cmd_options.log_level
        self.daemonize = cmd_options.daemonize
        self.only_check = cmd_options.only_check
        self.pid_file = cmd_options.pid_file
        self.script = cmd_options.script
        self.info_modules = cmd_options.info_modules
        self.interract = cmd_options.interract
        self.console = cmd_options.console
        self.rooms = []

        try:
            with open(conf_file) as f:
                data = yaml.load(f)
        except IOError as err:
            _abort("Unable to read the configuration file ‘%s’: %s.",
                   conf_file, err.strerror)
        except yaml.reader.ReaderError as err:
            _abort("The configuration file ‘%s’ seems incorrect or "
                   "corrupt: %s (position %s)", conf_file, err.reason,
                   err.position)
        except yaml.scanner.ScannerError as err:
            _abort("The configuration file seems incorrect or "
                   "corrupt: %s%s", err.problem, err.problem_mark)

        # Global configuration
        self.lang = 'en'
        self.logpath = "pipobot.log"
        global_conf = data.get('config', {})
        for param in ['logpath', 'lang']:
            value = global_conf.get(param, "")
            if not value or not isinstance(value, str):
                _abort("Required parameter ‘%s’ not found or invalid in "
                       "configuration file ‘%s’.", param, conf_file)
            setattr(self, param, value)

        self.xmpp_logpath = global_conf.get('xmpp_logpath', None)
        self.force_ipv4 = global_conf.get('force_ipv4', False)

        self.modules_path = global_conf.get('modules_path', [])
        if isinstance(self.modules_path, str):
            self.modules_path = [self.modules_path]
        elif type(self.modules_path) != list:
            _abort("Parameter ‘modules_path’ should be a string or a list in "
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
                    _abort("Parameter ‘src’ required for sqlite configuration "
                           "in file ‘%s’.", conf_file)
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

        for group_name, group_items in groups_conf.items():
            module_groups[group_name] = group = set()
            if type(group_items) != list:
                _abort("Parameter ‘groups[%s]’ should be a list in "
                       "configuration file ‘%s’.", group_name, conf_file)

            for group_item in group_items:
                if not isinstance(group_item, str):
                    _abort("Parameter ‘groups[%s]’ should only contain"
                           " strings in configuration file ‘%s’.", group_name,
                           conf_file)
                group.add(group_item)

        # Helper to load modules
        def _load_modules(conf_modules) :
            modules = set()

            if conf_modules is None:
                conf_modules = []
            elif isinstance(conf_modules, str):
                conf_modules = [conf_modules]

            for conf_module in conf_modules:
                if not isinstance(conf_module, str):
                    _abort("Parameter ‘modules’ should only contain"
                           " strings in configuration file ‘%s’.", conf_file)

                if not conf_module or conf_module == "_":
                    continue

                if conf_module[0] == '_':
                    name = conf_module[1:]
                    if name not in module_groups:
                        _abort("Unknown module group ‘%s’ for room "
                               "configuration ‘%s’ in configuration file ‘%s’.",
                               name, conf_file)

                    modules |= module_groups[name]

                else:
                    modules.add(conf_module)

            return modules

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
            protocol = conf_room.get('protocol', 'xmpp')
            kwargs = {'protocol': protocol}
            required_params = {'xmpp': ['resource', 'nick'],
                               'mattermost': ['address', 'default_channel', 'default_team'],
                               'matrix': ['address', 'chan'],
                               }
            for param in ['login', 'passwd'] + required_params[protocol]:
                value = conf_room.get(param, "")
                if not value or not isinstance(value, str):
                    if "chan" in kwargs:
                        _abort("Required parameter ‘rooms[%s][%s]’ not found or "
                               "invalid in configuration file ‘%s’.", kwargs[
                                   "chan"],
                               param, conf_file)
                    else:
                        _abort("One of your rooms needs a ‘chan‘ parameter")

                kwargs[param] = value

            kwargs['address'] = conf_room.get("address")

            port = conf_room.get('port')

            if port is not None:
                try:
                    port = int(port)
                except ValueError:
                    _info("Selected port %s is not valid : using default port 5222 instead", port)
                    port = 5222

            kwargs['port'] = port

            conf_modules = conf_room.get('modules')
            kwargs['modules'] = _load_modules(conf_modules)
            self.rooms.append(Room(**kwargs))

        # Tests
        test = data.get('test')
        if test :
            # Create new test room
            fake_nick = test.get('fake_nick', 'TestBot')
            fake_chan = test.get('fake_chan', 'chan@unknown.org')
            test_modules = _load_modules(test.get('modules'))
            self.test_room = Room(chan=fake_chan, login='invalid',
                                  passwd='invalid', resource='invalid',
                                  nick=fake_nick, modules=test_modules)
        else :
            self.test_room = None

        # Module parameters
        modules_conf = data.get('modules_config')
        if modules_conf is None:
            modules_conf = {}

        self.modules_conf = modules_conf


class Room(object):
    __slots__ = ('chan', 'login', 'passwd', 'resource', 'nick', 'modules', 'address', 'port', 'protocol',
                 'default_team', 'default_channel')

    def __init__(self, login, passwd, modules, resource=None, nick=None, chan=None, address=None, port=None,
                 default_team='', default_channel='', protocol='xmpp', ):
        self.chan = chan
        self.login = login
        self.passwd = passwd
        self.resource = resource
        self.nick = nick
        self.modules = modules
        self.address = address
        self.port = port
        self.protocol = protocol
        self.default_team = default_team
        self.default_channel = default_channel


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

    parser.add_option("--pid", dest="pid_file", type="string",
                      default=Configuration.DEFAULT_PIDFILE,
                      help="Specify a PID file (only used in background mode)")

    parser.add_option("--only-check", action="store_const",
                      dest="only_check", const=True, default=False,
                      help="Check if modules configuration are correct and exit")

    parser.add_option("--script", action="store",
                      dest="script", type="string", default="",
                      help="Run unit test defined in the config file")

    parser.add_option("--info-modules", action="store",
                      dest="info_modules", type="string", default="",
                      help="Shows descriptions of available modules")

    parser.add_option("--interract", action="store_const",
                      dest="interract", const=True,
                      help="Run the twisted bot")

    parser.add_option("--console", action="store_const",
                      dest="console", const=True,
                      help="Run a Python interpretor with the bot and all modules loaded")

    (options, args) = parser.parse_args()
    parser.destroy()

    conf_file = args[0] if len(args) > 0 else Configuration.DEFAULT_CONF_FILE

    return Configuration(options, conf_file)
