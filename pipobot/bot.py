# -*- coding: utf-8 -*-
import logging
from pipobot.lib.modules import (AsyncModule, ListenModule,
                                 MultiSyncModule, PresenceModule,
                                 SyncModule, IQModule)
from pipobot.lib.user import Occupants

logger = logging.getLogger('pipobot.pipobot')


class PipoBot:
    def __init__(self, name, login, chatname, modules, session):
        self.name = name
        self.login = login
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
            if isinstance(obj, AsyncModule):
                obj.start()
                self.async_mods.append(obj)
            # Not an elif here because some modules can be Async *and* Sync
            if isinstance(obj, SyncModule):
                self.sync_mods.append(obj)
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

    @property
    def modules(self):
        return (self.async_mods + self.iq_mods + self.listen_mods +
                self.multisync_mods + self.presence_mods + self.sync_mods)

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

    def gen_xhtml(self, send):
        """ Creates messages with a dictionnary described as :
               {"text": raw_message,    # Text message, transform XHTML if empty
                "xhtml" : xhtml_message # XHTML message
                "monospace" : True      # XHTML message is the text with monospace
                "users" : { "pseudo1" : {...} } # Send the same type of dictionnary
                                                  in private to the users
               }"""
        if "xhtml" not in send and "text" in send and "monospace" in send and send["monospace"]:
            html_msg = send["text"]
            html_msg = html_msg.replace("&", "&amp;")
            html_msg = html_msg.replace("<", "&lt;")
            html_msg = html_msg.replace(">", "&gt;")
            html_msg = '<p><span style="font-family: monospace">%s</span></p>' % html_msg.replace("\n", "<br/>\n")
            #TODO others characters to convert ?
            send["xhtml"] = html_msg
        return send
