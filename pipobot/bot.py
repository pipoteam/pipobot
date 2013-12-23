# -*- coding: utf-8 -*-
import logging
import traceback
from pipobot.lib.modules import (AsyncModule, base_class)
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.pipobot')


class Modules(object):
    def __init__(self):
        for modtype in base_class:
            setattr(self, modtype.shortname, {})

    def add_mod(self, mod):
        short_type = mod.shortname
        getattr(self, short_type)[mod.name] = mod
        if isinstance(mod, AsyncModule):
            mod.start()
            getattr(self, AsyncModule.shortname)[mod.name] = mod
        # Not an elif here because some modules can be Async *and* Sync
        for klass in base_class:
            if isinstance(mod, klass):
                getattr(self, klass.shortname)[mod.name] = mod

    def get_all(self):
        ret = []
        for klass in base_class:
            ret.extend(getattr(self, klass.shortname).values())
        return ret

    def find(self, name):
        for klass in base_class:
            try:
                return getattr(self, klass.shortname)[name]
            except KeyError:
                pass


class PipoBot:
    def __init__(self, name, login, chatname, modules, session):
        self.name = name
        self.login = login
        self.chatname = chatname
        self.session = session

        self._modules = Modules()

        for classe in modules:
            try:
                obj = classe(self)
            except:
                msg = _("An exception was raised starting module %s for room %s : %s")
                msg %= (classe, chatname, traceback.format_exc().decode("utf-8"))
                logger.error(msg)
                continue
            self._modules.add_mod(obj)

        self.mute = False
        self.occupants = Occupants()

    @property
    def modules(self):
        return self._modules.get_all()

    def stop_modules(self):
        logger.info(u"Killing %s" % self.chatname)
        for module in self._modules.async.values():
            module.stop()

    def module_answer(self, mess):
        # First we look if a SyncModule matches
        if self.mute:
            return

        for module in self._modules.sync.values() + self._modules.multisync.values():
            ret = module.do_answer(mess)
            if ret is not None:
                return ret

        result = []
        # If no SyncModule was concerned by the message, we look for a ListenModule
        for module in self._modules.listen.values():
            ret = module.do_answer(mess)
            if ret is not None:
                result.append(ret)

        return result

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False

