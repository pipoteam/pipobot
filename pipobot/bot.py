# -*- coding: utf-8 -*-
import logging
from pipobot.lib.modules import (AsyncModule, ListenModule,
                                 MultiSyncModule, PresenceModule,
                                 SyncModule, IQModule)
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.pipobot')


class PipoBot:
    def __init__(self, name, chatname, modules, session):
        self.name = name
        self.chatname = chatname
        self.session = session

        self.async_mods = []
        self.iq_mods = []
        self.listen_mods = []
        self.multisync_mods = []
        self.presence_mods = []
        self.sync_mods = []

        for classe in modules:
            obj = classe(self)
            if isinstance(obj, SyncModule):
                self.sync_mods.append(obj)
            elif isinstance(obj, AsyncModule):
                obj.start()
                self.async_mods.append(obj)
            elif isinstance(obj, ListenModule):
                self.listen_mods.append(obj)
            elif isinstance(obj, MultiSyncModule):
                self.multisync_mods.append(obj)
            elif isinstance(obj, PresenceModule):
                self.presence_mods.append(obj)
            elif isinstance(obj, IQModule):
                self.iq_mods.append(obj)

        self.mute = False
        self.occupants = Occupants()

    def stop_modules(self):
        logger.info(u"Killing %s" % self.chatname)
        for module in self.async_mods:
            module.stop()

    def module_answer(self, mess):
        # First we look if a SyncModule matches
        if self.mute:
            return

        for module in self.sync_mods + self.multisync_mods:
            ret = module.do_answer(mess)
            if ret is not None:
                return ret

        result = []
        # If no SyncModule was concerned by the message, we look for a ListenModule
        for module in self.listen_mods:
            ret = module.do_answer(mess)
            if ret is not None:
                result.append(ret)

        return result

    def disable_mute(self):
        """To give the bot its voice again"""
        self.mute = False
