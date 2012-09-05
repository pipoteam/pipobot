#!/usr/bin/python
# -*- coding: UTF-8 -*-
import inspect
import imp
import logging
import sys
from pipobot.lib.modules import Help, RecordUsers, BotModule
from pipobot.lib.known_users import KnownUsersManager

logger = logging.getLogger('pipobot.lib.loader')


class BotModuleLoader(object):
    def __init__(self, extra_modules_paths=None, modules_settings=None):
        self._paths = []

        if extra_modules_paths:
            self._paths.extend(extra_modules_paths)

        self._module_settings = modules_settings or {}
        self._module_cache = {}

    @staticmethod
    def is_bot_module(obj):
        """
        Returns True if an object found in a Python module is a bot module
        class.
        """

        return (inspect.isclass(obj) and issubclass(obj, BotModule)
                and not hasattr(obj, '_%s__usable' % obj.__name__))

    def get_modules(self, module_names):
        modules = []

        for name in module_names:
            if name in self._module_cache:
                modules.extend(self._module_cache[name])
                continue

            try:
                module_info = imp.find_module(name, self._paths)
            except ImportError:
                sys.stderr.write("Module ‘%s’ was not found.\n" % name)
                sys.exit(1)

            module_data = imp.load_module(name, *module_info)
            bot_modules = inspect.getmembers(module_data, self.is_bot_module)
            bot_modules = [item[1] for item in bot_modules]

            #We search for _config parameter (ie required configuration parameter) in each module
            for module in bot_modules:
                if hasattr(module, "_config"):
                    #If there is a configuration section in config file for this module
                    if name in self._module_settings:
                        #We check all required parameters
                        for (param_name, param_type) in module._config:
                            #If the parameter is defined in the configuration file
                            if param_name in self._module_settings[name]:
                                config_param = self._module_settings[name][param_name]
                                #If the configuration section is well defined
                                if type(config_param) == param_type:
                                    setattr(module, param_name, config_param)
                                else:
                                    #In case of failure, we create an empty parameter with the good type
                                    setattr(module, param_name, param_type())
                                    logger.error(("Parameter %s of configuration of module %s must be a %s, but is "
                                                  "currently a %s") % (param_name,
                                                                        name,
                                                                        param_type.__name__,
                                                                        type(config_param).__name__))
                            else:
                                setattr(module, param_name, param_type())
                                logger.error("Configuration of %s requires %s parameter" % (name,
                                                                                            param_name))

                    else:
                        logger.error("Missing configuration for module %s" % name)
                        for (param_name, param_type) in module._config:
                            #In case of failure, we create an empty parameter with the good type
                            setattr(module, param_name, param_type())

            if name in self._module_settings:
                logger.debug("Configuration for ‘%s’: %s", name,
                             self._module_settings[name])
                for module in bot_modules:
                    module._settings = self._module_settings[name]

            logger.debug("Bot modules for ‘%s’ : %s", name, bot_modules)

            modules.extend(bot_modules)
            self._module_cache[name] = bot_modules

        modules.append(RecordUsers)
        modules.append(Help)
        KnownUsersManager._settings = {}
        if "user" in self._module_settings:
            KnownUsersManager._settings = self._module_settings["user"]

        modules.append(KnownUsersManager)
        return modules
