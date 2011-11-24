#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

class Occupants:
    def __init__(self):
        self.users = {}
        self.logger = logging.getLogger("pipobot.users")
    
    def add_user(self, nickname, jid, role):
        u = User(nickname, jid, role)
        self.users[nickname] = u

    def rm_user(self, nickname):
        try:
            del self.users[nickname]
        except KeyError:
            #Removing a user not in the room… should never happen
            pass

    def get_all(self, separator, exceptions = []):
        return separator.join([user.nickname for user in self.users.itervalues() if user not in exceptions])
        
    def pseudo_to_jid(self, pseudo):
        try:
            return self.users[pseudo].jid
        except KeyError:
            self.logger.error(_("The user %s is not in the room !") % pseudo)
            return ""

    def pseudo_to_role(self, pseudo):
        try:
            return self.users[pseudo].power
        except KeyError:
            self.logger.error(_("The user %s is not in the room !") % pseudo)
            return ""

    def jid_to_pseudo(self, jid):
        for user in self.users.itervalues():
            if user.jid == jid:
                return user
        self.logger.error(_("The user with jid %s is not in the room !") % jid)
        return jid

class User:
    def __init__(self, nickname, jid, role):
        self.nickname = nickname
        self.jid = jid
        self.role = role
