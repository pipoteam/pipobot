#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pipobot.lib.bdd import Base
from pipobot.lib.modules import SyncModule, defaultcmd, answercmd

class KnownUser(Base):
    __tablename__ = "knownuser"
    pseudo = Column(String(250), primary_key=True)
    permlvl = Column(Integer) # Permissions level 1: none, 2: moderator, 3: super-moderator, 4: admin, 5: super-admin
    hllvl = Column(Integer) # HighlightLevel 1: never, 2: sometimes, 3: always
    jids = relationship("KnownUsersJIDs", backref="knownuser")

    def __init__(self, pseudo, permlvl=1, hllvl=3, jids=[]):
        self.pseudo = pseudo
        self.permlvl = permlvl
        self.hllvl = hllvl

class KnownUsersJIDs(Base):
    __tablename__ = "knownusersjids"
    jid = Column(String(250), primary_key=True)
    users_pseudo = Column(String(250), ForeignKey('knownuser.pseudo'))
    user = relationship(KnownUser, primaryjoin=users_pseudo == KnownUser.pseudo)

    def __init__(self, jid, pseudo):
        self.jid = jid
        self.users_pseudo = pseudo

class KnownUsersManager(SyncModule):
    def __init__(self, bot):
        desc  =   "user : shows this help"
        desc += "\nuser register args: register user <pseudo> (defaults: you) with JID(s) <jid(s)> (defaults: your JID)"
        desc += "\nuser show: prints the whole Knows Users database"
        desc += "\nuser show pseudo: prints informations about <pseudo> (can also be 'me')"
        desc += "\nuser hllvl [pseudo]: prints the Highlight Level of <pseudo> (defaults: you)"
        desc += "\nuser hllvl [pseudo] lvl [pseudo]: sets the Highlight Level of <pseudo> (defaults: you) to <lvl>"
        desc += "\nuser permlvl [pseudo]: prints the Permission Level of <pseudo> (defaults: you)"
        desc += "\nuser permlvl [pseudo] lvl [pseudo]: sets the Permission Level of <pseudo> (defaults: you) to <lvl>"
        SyncModule.__init__(self,
                bot,
                desc = desc,
                command = "user")

        self.desc = desc
        self.logger = logging.getLogger("pipobot.knownusers")

        try:
            for admin in bot.settings["config"]["admins"]:
                user = ''
                if '@' in admin:
                    usersjid = self.bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == admin).first()
                    user = usersjid.user
                else:
                    user = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == admin).first()
                if user:
                    user.permlvl = 5
                    bot.session.commit()
                else:
                    self.logger.error(_('Admin %s is not yet registered !' % admin))
        except KeyError:
            self.logger.error(_('You shall add an admin section in your configuration file'))



    @answercmd(r'^register')
    def answer_register(self, sender, message):
        pseudo = ''
        jids = []
        for m in message.string.strip().split(' ')[1:]:
            if '@' in m:
                jids.append(m)
            else:
                pseudo = m
        if not pseudo:
            pseudo = sender
        if not jids:
            jids.append(self.bot.occupants.pseudo_to_jid(sender))

        targetuser = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == pseudo).first()
        senderuser = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == sender).first()

        if not targetuser:
            targetuser = KnownUser(pseudo = pseudo, jids = jids)
            self.bot.session.add(targetuser)
        elif senderuser.permlvl <= targetuser.permlvl:
            return _("%s: %s is already registered, and you can't modify his settings" % (senderuser.pseudo, targetuser.pseudo))

        for jid in jids:
            check = self.bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == jid).first()
            if check:
                targetuser = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == check.users_pseudo).first()
                ret = "%s: %s est associé aux JID(s) " % (sender, check.users_pseudo)
                for jid in targetuser.jids:
                    ret += '%s ' % jid.jid
                return ret
            j = KnownUsersJIDs(jid, pseudo)
            self.bot.session.add(j)
        self.bot.session.commit()

        return _("pseudo %s associated to jid(s) %s" % (pseudo,jids))

    @answercmd(r'^show')
    def answer_show(self, sender, message):
        user = ''
        if message.string[5:] == 'me':
            user = sender
        elif message.string[5:]:
            user = message.string[5:].strip()
        if user:
            knownuser = ''
            if '@' not in user:
                knownuser = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == user).first()
            if not knownuser:
                if '@' not in user:
                    user = self.bot.occupants.pseudo_to_jid(user)
                user = self.bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == user).first().users_pseudo
                knownuser = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == user).first()
            if not knownuser:
                return _('You are not identified')
            ret = _('%s: Your Highlight Level is %i, your Permission Level is %s, and your JID(s) are:' %(knownuser.pseudo, knownuser.hllvl, knownuser.permlvl))
            for jid in knownuser.jids:
                ret += ' %s' % jid.jid
            return ret
        ret = _('Registered users:')
        users = self.bot.session.query(KnownUser).all()
        for user in users:
            ret += "\n  %-30s %s %s " % (user.pseudo, user.permlvl, user.hllvl)
            for jid in user.jids:
                ret += '%s ' % jid.jid
        return ret

    @answercmd(r'^(hl|perm)lvl')
    def answer_lvl(self, sender, message):
        lvl = 0
        pseudo = ''
        lvltype = message.group()
        for m in message.string.strip().split(' ')[1:]:
            try:
                lvl = int(m)
            except ValueError:
                pseudo = m
        if not pseudo:
            pseudo = sender
        user = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == pseudo).first()
        if not user:
            user = self.bot.session.query(KnownUser).filter(KnownUsersJIDs.jid == self.bot.occupants.pseudo_to_jid(pseudo)).first()
        if not user:
            return _("I don't know you, %s…" % sender)
        if not lvl:
            if lvltype == 'hllvl':
                return _('%s: Your Highlight Level is %i' % (sender, user.hllvl))
            return _('%s: Your Permission Level is %i' % (sender, user.permlvl))

        sender = self.bot.session.query(KnownUser).filter(KnownUser.pseudo == sender).first()
        if sender.permlvl < user.permlvl:
            return _('%s: you have less permissions than %s here…' % (sender.pseudo, user.pseudo))
        if sender != user and sender.permlvl < 2:
            return _("%s: you don't have the right permissons to do that." % sender.pseudo)
        if lvltype == 'permlvl' and sender != user and sender.permlvl == user.permlvl:
            return _("%s: %s and you got the same Permission Level, so you can't change it." % (sender.pseudo, user.pseudo))
        if lvltype == 'permlvl' and lvl > sender.permlvl:
            return _("%s: No, you can't give more rights than you have…" % sender.pseudo)

        if lvltype == 'hllvl':
            user.hllvl = lvl
        else:
            user.permlvl = lvl
        self.bot.session.commit()

        if lvltype == 'hllvl':
            return _("%s's Highlight Level modified to %i" % (pseudo, lvl))
        return _("%s's Permission Level modified to %i" % (pseudo, lvl))

    @defaultcmd
    def answer(self, sender, args) :
        return self.desc

