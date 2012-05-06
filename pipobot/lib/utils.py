#! /usr/bin/python
#-*- coding: utf-8 -*-

import re, htmlentitydefs
import xmpp

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def xhtml2text(html):
#fonction de conversion xHTML -> texte pour les clients
#ne supportant pas la XEP-0071
    # on symbolise le gras par "*"
    html = re.sub('<[^>]*b>', '*', html)
    html = re.sub('<[^>]*strong>', '*', html)
    # le souligné par "_"
    html = re.sub('<[^>]*u>', '_', html)
    # on enlève toutes les autres balises
    #TODO: récuppérer le lien dans les balises <a>
    html = re.sub('<[^>]*>', '', html)

    return unescape(html)

def kick(toKick, msg, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns","http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toKick)
    itemchild.setAttr("role","none")

    reason = itemchild.addChild("reason")
    reason.addData(msg)
    bot.send(iq)

def mute(toKick, msg, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns","http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toKick)
    itemchild.setAttr("role","visitor")
    reason = itemchild.addChild("reason")
    reason.addData(msg)
    bot.send(iq)

def unmute(toMute, bot):
    iq = xmpp.Iq(typ="set",
                 to=bot.chat)
    querychild = iq.addChild('query')
    querychild.setAttr("xmlns","http://jabber.org/protocol/muc#admin")
    itemchild = querychild.addChild("item")
    itemchild.setAttr("nick", toMute)
    itemchild.setAttr("role","participant")
    bot.send(iq)
