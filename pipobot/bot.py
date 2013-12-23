# -*- coding: utf-8 -*-
import logging
import traceback
from pipobot.lib.modules import AsyncModule, base_class
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.pipobot')


class Modules(object):
    def __init__(self):
        for modtype in base_class:
            setattr(self, modtype.shortname, [])

    def add_mod(self, mod):
        # Not an elif here because some modules can be Async *and* Sync
        for klass in base_class:
            if isinstance(mod, klass):
                if klass is AsyncModule:
                    mod.start()
                getattr(self, klass.shortname).append(mod)

    def get_all(self):
        ret = []
        for klass in base_class:
            ret.extend(getattr(self, klass.shortname))
        return ret

    def find(self, name):
        for klass in base_class:
            for mod in getattr(self, klass.shortname):
                if mod.name == name:
                    return mod

    def stop(self):
        for module in self.async:
            module.stop()


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

    def __getattr__(self, name):
        """ Proxy to have access to modules with :
            - self.sync
            - self.async
            - self.presence
            …
        """
        if name in [klass.shortname for klass in base_class]:
            return getattr(self._modules, name)

    def stop_modules(self):
        logger.info(u"Killing %s" % self.chatname)
        self._modules.stop()

    def module_answer(self, mess):
        """ Given a text message, try each registered module for an answer.
            - Sync & Multisync first
            - If no module answered, try every known ListenModule
        """
        # First we look if a SyncModule matches
        if self.mute:
            return

        for module in self.sync + self.multisync:
            ret = module.do_answer(mess)
            if ret is not None:
                return ret

        result = []
        # If no SyncModule was concerned by the message, we look for a ListenModule
        for module in self.listen:
            ret = module.do_answer(mess)
            if ret is not None:
                result.append(ret)

        return result

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False
