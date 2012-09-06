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

    def get_modules(self, module_names, check=False):
        modules = []

        for name in module_names:
            if name in self._module_cache:
                modules.extend(self._module_cache[name])
                continue

            try:
                module_info = imp.find_module(name, self._paths)
            except ImportError:
                logger.error(("Module ‘%s’ was not found." % name))
                if check:
                    continue
                else:
                    sys.exit(1)

            module_data = imp.load_module(name, *module_info)
            bot_modules = inspect.getmembers(module_data, self.is_bot_module)
            bot_modules = [item[1] for item in bot_modules]

            #We search for _config parameter (ie required configuration parameter) in each module
            for module in bot_modules:
                if not hasattr(module, "_config"):
                    continue
                #For each config parameter specified in the module
                for (param_name, param_type, default_value) in module._config:
                    #if the parameter is defined in the config file
                    if name in self._module_settings and param_name in self._module_settings[name]:
                        config_param = self._module_settings[name][param_name]
                        #If the parameter defined in the config file does not have the good structure
                        if type(config_param) != param_type:
                            #an empty value of type param_type
                            logger.error(_("Parameter ‘%s‘ of configuration of module ‘%s‘ must be a %s, but is "
                                           "currently a %s") % (param_name,
                                                                name,
                                                                param_type.__name__,
                                                                type(config_param).__name__))
                            #In case of failure, we use a default_value if provided, else
                            config_param = param_type() if default_value is None else default_value
                    else:
                        #The parameter is not defined in the config file
                        #We use default_value if provided (not None), else an empty value of type param_type
                        if default_value is None:
                            logger.error(_("Configuration of ‘%s‘ requires ‘%s‘ parameter") % (name,
                                                                                           param_name))
                            config_param = param_type()
                        else:
                            config_param = default_value
                            logger.info(_("Optional parameter for module ‘%s‘ : ‘%s‘ (default value ‘%s‘ will be used)") % (name,
                                                                                                                       param_name,
                                                                                                                       config_param))

                    setattr(module, param_name, config_param)

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
