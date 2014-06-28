# !/usr/bin/python
# -*- coding: utf-8 -*-
"""This file contains the class 'BotJabber' which is a bot for jabber MUC"""

import logging
import sleekxmpp
import threading
import time

from pipobot.bot import PipoBot

logger = logging.getLogger('pipobot.bot_jabber')


class XMPPException(Exception):
    """ For errors due to XMPP (conflict, connection/authentification failed, …) """
    pass


XML_NAMESPACE = 'http://www.w3.org/1999/xhtml'
_muc_xml = "{http://jabber.org/protocol/muc# user}status"


class BotJabber(sleekxmpp.ClientXMPP, PipoBot):
    """The implementation of a bot for jabber MUC"""

    def __init__(self, login, passwd, res, chat, name, modules, session, force_ipv4, address=None, port=None):
        sleekxmpp.ClientXMPP.__init__(self, "%s/%s" % (login, res), passwd)

        port = port if port is not None else 5222
        address = address if address is not None else self.boundjid.host

        address = (address, port)

        logger.info("Connecting to %s", chat)
        self.use_ipv6 = not force_ipv4
        # Connecting
        con = self.connect(address=address, reattempt=False)
        if not con:
            logger.error(_("Unable to connect !"))
            raise XMPPException(_("Unable to connect !"))

        self.registerPlugin("xep_0045")

        # When the session start (bot connected) the connect_muc method will be called
        self.add_event_handler("session_start", self.connect_muc)

        # sleekxmpp handlers to XMPP stanzas
        self.add_event_handler("message", self.message_handler)
        self.add_event_handler("groupchat_presence", self.presence_handler)
        self.add_event_handler("failed_auth", self.failed_auth)

        PipoBot.__init__(self, name, login, chat, modules, session)

        self.process(threaded=True)

    def failed_auth(self, event):
        logger.error(_("Unable to authenticate !"))

    def connect_muc(self, event):
        self.send_presence()
        muc = self.plugin["xep_0045"]
        muc.joinMUC(self.chatname, self.name)
        hello_msg = _("Hello everyone !")
        self.send_message(mto=self.chatname, mbody=hello_msg, mtype="groupchat")

    def message_handler(self, mess):
        """Method called when the bot receives a message"""
        # We ignore messages in some cases :
        #   - the bot is muted
        #   - it has a subject (change of room topic for instance)
        #   - the message is empty
        if self.mute                 \
            or mess["subject"] != ""  \
            or mess["body"] == "":
            return

        super(BotJabber, self).message_handler(mess)

    def answer(self, mess):
        result = self.module_answer(mess)
        if type(result) is list:
            for to_send in result:
                self.say(to_send, in_reply_to=mess)
        else:
            self.say(result, in_reply_to=mess)

    def kill(self):
        """Method used to kill the bot"""

        # The bot says goodbye
        self.say(_("I’ve been asked to leave you"))
        # The bot leaves the room
        self.disconnect(wait=True)
        self.stop_modules()

    def forge_message(self, mess, priv=None, in_reply_to=None):
        """Method used to send a message in a the room"""

        mto = self.chatname
        mtyp = "groupchat"

        if priv:
            mto = "%s/%s" % (self.chatname, priv)
            mtyp = "chat"

        if in_reply_to:
            mtyp = in_reply_to["type"]
            if mtyp == "chat":
                mto = in_reply_to["from"]

        msg = self.make_message(mto, mbody=mess, mtype=mtyp)
        return msg

    def forge(self, mess, priv=None, in_reply_to=None):
        """Sending an xhtml message in the room"""

        # It is an XHTML message !
        # The message is created from mess, in case some clients does not support XHTML (xep-0071)
        if type(mess) is dict:
            if "xhtml" not in mess:
                mess = self.gen_xhtml(mess)

            if "nopriv" in mess:
                priv = None
                in_reply_to = None

            msg = self.forge_message(mess["text"],
                                     priv=priv,
                                     in_reply_to=in_reply_to)
            if "xhtml" in mess:
                mess_xhtml = mess["xhtml"]
                mess_xhtml = "<p>%s</p>" % mess_xhtml
                if type(mess_xhtml) is str:
                    mess_xhtml = mess_xhtml
                msg["html"]["body"] = mess_xhtml
        else:
            msg = self.forge_message(mess, priv=priv, in_reply_to=in_reply_to)
        return msg

    def say(self, msg, priv=None, in_reply_to=None):
        """The method to call to make the bot sending messages"""
        # If the bot has not been disabled
        if not self.mute:
            if type(msg) is str or type(msg) is str:
                self.forge(msg, priv=priv, in_reply_to=in_reply_to).send()
            elif type(msg) is list:
                for line in msg:
                    time.sleep(0.3)
                    self.forge(line, priv=priv, in_reply_to=in_reply_to).send()
            elif type(msg) is dict:
                if not "users" in msg:
                    self.forge(msg, priv=priv, in_reply_to=in_reply_to).send()
                else:
                    # Syntax for this type of messages is :
                    # {"users": {"user1": msg1,
                    #            "user2": msg2}}
                    # so user1(2) will receive in private msg1(2)
                    # msg1(2) can be 'complex' messages (list, dict, unicode, str)
                    # Private / non private messages can be "mixed" if for instance
                    # msg1 = {"text": "some_text", "nopriv": True}
                    for user, send_user in msg["users"].items():
                        self.say(send_user, priv=user)

    def presence_handler(self, mess):
        """Method called when the bot receives a presence message.
           Used to record users in the room, as well as their jid and roles"""
        try:
            code = mess["muc"].find(_muc_xml).get("code")
            code = int(code)
            if code == 110:
                self.name = mess["muc"]["nick"]
        except AttributeError:
            # No "status code" in the message
            pass

        for module in self.presence:
            module.do_answer(mess)

    def iq_handler(self, conn, iqdata):
        """Method called when the bot receives an IQ message"""
        for module in self.iq:
            module.do_answer(iqdata)

    def gen_xhtml(self, send):
        """ Creates messages with a dictionnary described as :
        {"text": raw_message,    # Text message, transform XHTML if empty
        "xhtml" : xhtml_message # XHTML message
        "monospace" : True      # XHTML message is the text with monospace
        "users" : { "pseudo1" : {...} } # Send the same type of dictionnary
        #                                           in private to the users
        }
		"""
        if "xhtml" not in send and "text" in send and "monospace" in send and send["monospace"]:
            html_msg = send["text"]
            html_msg = html_msg.replace("&", "&amp;")
            html_msg = html_msg.replace("<", "&lt;")
            html_msg = html_msg.replace(">", "&gt;")
            html_msg = '<p><span style="font-family: monospace">%s</span></p>' % html_msg.replace("\n", "<br/>\n")
            #TODO others characters to convert ?
            send["xhtml"] = html_msg
        return send
