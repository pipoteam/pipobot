#!/usr/bin/python
# -*- coding: UTF-8 -*-
import inspect
import imp
import logging
import sys
import unittest
import traceback
from collections import namedtuple

from pipobot.lib.modules import Help, RecordUsers, BotModule
from pipobot.lib.known_users import KnownUsersManager
from pipobot.lib.module_test import ModuleTest

logger = logging.getLogger('pipobot.lib.loader')


class BotModuleLoader(object):
    def __init__(self, modules_paths=None, modules_settings=None):
        self._paths = []

        if modules_paths:
            self._paths.extend(modules_paths)

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

    @staticmethod
    def is_test_unit(obj):
        """
        Returns True if an object found in a Python module is a test unit
        class.
        """

        return (inspect.isclass(obj) and issubclass(obj, ModuleTest)
                and not hasattr(obj, '_%s__usable' % obj.__name__))

    def set_module_config(self, module_name, param_name, param_type, default_value):
        # if the parameter is defined in the config file
        if module_name in self._module_settings and param_name in self._module_settings[module_name]:
            config_param = self._module_settings[module_name][param_name]
            # If the parameter defined in the config file does not have the good structure
            if type(config_param) != param_type:
                #an empty value of type param_type
                logger.error(_("Parameter ‘%s‘ of configuration of module ‘%s‘ must be a %s, but is "
                               "currently a %s") % (param_name,
                                                    module_name,
                                                    param_type.__name__,
                                                    type(config_param).__name__))
                # In case of failure, we use a default_value if provided, else
                config_param = param_type() if default_value is None else default_value
        else:
            # The parameter is not defined in the config file
            # We use default_value if provided (not None), else an empty value of type param_type
            if default_value is None:
                logger.error(_("Configuration of ‘%s‘ requires ‘%s‘ parameter") % (module_name,
                                                                                   param_name))
                config_param = param_type()
            else:
                config_param = default_value
                logger.info(_("Optional parameter for module ‘%s‘ : ‘%s‘ "
                              "(default value ‘%s‘ will be used)") % (module_name,
                                                                      param_name,
                                                                      config_param))

        return config_param

    def get_modules(self, module_names):
        modules_tpl = namedtuple('modules_tpl', ['modules', 'test_mods'])
        modules = []
        test_modules = []

        error = 0

        for name in module_names:
            if name in self._module_cache:
                modules.extend(self._module_cache[name])
                continue

            try:
                module_info = imp.find_module(name, self._paths)
            except ImportError:
                logger.error(("Module ‘%s’ was not found." % name))
                error += 1
                continue

            try:
                module_data = imp.load_module(name, *module_info)
            except ImportError:
                logger.error(("Module ‘%s’ could not be imported." % name))
                logger.error(traceback.format_exc())
                error += 1
                continue

            test_modules.extend(elt[1] for elt in inspect.getmembers(module_data, self.is_test_unit))

            bot_modules = inspect.getmembers(module_data, self.is_bot_module)
            bot_modules = [item[1] for item in bot_modules]

            # We search for _config parameter (ie required configuration parameter) in each module
            for module in bot_modules:
                if hasattr(module, "_config"):
                    # For each config parameter specified in the module
                    for (param_name, param_type, default_value) in module._config:
                        config_param = self.set_module_config(name, param_name, param_type, default_value)
                        setattr(module, param_name, config_param)

            logger.debug("Bot modules for ‘%s’ : %s", name, bot_modules)

            modules.extend(bot_modules)
            self._module_cache[name] = bot_modules

        modules.append(RecordUsers)
        modules.append(Help)
        KnownUsersManager._settings = {}
        if "user" in self._module_settings:
            KnownUsersManager._settings = self._module_settings["user"]

        modules.append(KnownUsersManager)
        return error, modules_tpl(modules, test_modules)
