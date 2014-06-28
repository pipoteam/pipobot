# -*- coding: utf-8 -*-
import logging
import threading
import traceback
from pipobot.lib.modules import AsyncModule, base_class
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.pipobot')


class Modules(object):
    def __init__(self):
        for modtype in base_class:
            setattr(self, modtype.shortname, [])

    def add_mod(self, mod, bot):
        try:
            mod = mod(bot)
        except:
            msg = _("An exception was raised starting module %s for room %s : %s")
            msg %= (mod, bot.chatname, traceback.format_exc())
            logger.error(msg)
            return
        for klass in base_class:
            if isinstance(mod, klass):
                if klass is AsyncModule:
                    mod.start()
                getattr(self, klass.shortname).append(mod)

    def __iter__(self):
        for klass in base_class:
            for mod in getattr(self, klass.shortname):
                yield mod

    def find(self, name):
        for mod in self:
            if mod.name == name:
                return mod

    def stop(self):
        """ Stop all async modules registered """
        for module in self.async:
            module.stop()

    def sync_answer(self, msg):
        """ Try to find a SyncModule, or a MultiSyncModule that answers the `msg` """
        for module in self.sync + self.multisync:
            ret = module.do_answer(msg)
            if ret is not None:
                return ret

    def listen_answer(self, msg):
        """ Try to find all ListenModule that answer the `msg` """
        result = []
        for module in self.listen:
            ret = module.do_answer(msg)
            if ret is not None:
                result.append(ret)
        return result


class PipoBot:
    def __init__(self, name, login, chatname, modules, session):
        self.name = name
        self.login = login
        self.chatname = chatname
        self.session = session

        self.mute = False
        self._modules = Modules()
        for classe in modules:
            self._modules.add_mod(classe, self)
        self.occupants = Occupants()

    @property
    def modules(self):
        return self._modules

    def __getattr__(self, name):
        """ Proxy to have access to modules with :
            - self.sync
            - self.async
            - self.presence
            …
        """
        if name in [klass.shortname for klass in base_class]:
            try:
                return getattr(self._modules, name)
            except AttributeError:
                return

    def stop_modules(self):
        logger.info("Killing %s", self.chatname)
        self._modules.stop()

    def message_handler(self, msg):
        """Method called when the bot receives a message"""
        thread = threading.Thread(target=self.answer, args=(msg,))
        thread.start()
        return thread

    def module_answer(self, msg):
        """ Given a text message, try each registered module for an answer.
            - Sync & Multisync first
            - If no module answered, try every known ListenModule
        """
        if self.mute:
            return

        # First we look if a SyncModule or a MultiSyncModule matches
        sync = self._modules.sync_answer(msg)
        if sync is not None:
            return sync

        # Else we try listen modules
        return self._modules.listen_answer(msg)

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False
