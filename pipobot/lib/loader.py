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
