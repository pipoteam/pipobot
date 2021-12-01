#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from pipobot.lib.bdd import Base
from pipobot.lib.modules import Pasteque, SyncModule, answercmd, defaultcmd
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship


def minpermlvl(lvl):
    def wrapper(fct):
        def wrapped(self, sender, *args, **kwargs):
            user = KnownUser.get(sender, self.bot, authviapseudo=False)
            if not user:
                return _("%s: You are not even registered…" % sender)
            if user.get_permlvl(self.bot.chatname) < lvl:
                return _("%s: You need a permlvl of %i to do that." % (sender, lvl))
            return fct(self, sender, *args, **kwargs)
        return wrapped
    return wrapper


class PerChanPermissions(Base):
    __tablename__ = 'per_chan_permissions'
    knownuser_kuid = Column(Integer, ForeignKey('knownuser.kuid'), primary_key=True)
    chans_cid = Column(Integer, ForeignKey('chans.cid'), primary_key=True)
    permlvl = Column(Integer)
    chan = relationship("Chans")

    def __init__(self, permlvl):
        self.permlvl = permlvl

    def __repr__(self):
        return _("%i on %s" % (self.permlvl, self.chan.name))


class KnownUser(Base):
    __tablename__ = "knownuser"
    kuid = Column(Integer, primary_key=True)
    pseudo = Column(String(250), unique=True)
    hl_pseudo = Column(String(250))
    permlvl = Column(Integer)  # Permissions level 1: none, 2: moderator, 3: super-moderator, 4: admin, 5: super-admin
    jids = relationship("KnownUsersJIDs", backref="knownuser")
    chanperms = relationship("PerChanPermissions")

    def __init__(self, pseudo, permlvl=1):
        self.pseudo = pseudo
        self.permlvl = permlvl

    def __str__(self):
        return self.get_pseudo()

    def get_pseudo(self, hl=False):
        if not hl and self.hl_pseudo is not None:
            return self.hl_pseudo
        return self.pseudo

    def get_permlvl(self, chan):
        for scp in self.chanperms:
            if scp.chan.name == chan:
                if scp.permlvl > self.permlvl:
                    return scp.permlvl
                break
        return self.permlvl

    def has_the_power_on(self, other, chan):
        if not other:
            return True
        if self == other:
            return True

        selfpermlvl = self.get_permlvl(chan)
        otherpermlvl = other.get_permlvl(chan)

        if selfpermlvl > otherpermlvl:
            return True
        return False

    @staticmethod
    def get(pseudo, bot, authviapseudo=False, avoid_bot=True):
        if avoid_bot and pseudo == bot.name:
            raise Pasteque(_("Hey, that's me ! I'm not an user, I'm the bot !"))
        if '@' in pseudo:
            usersjid = bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == pseudo).first()
            if usersjid:
                return usersjid.user
            else:
                return None
        # Authentication via pseudo… Looks like it's not secure enough ;)
        if authviapseudo:
            user = bot.session.query(KnownUser).filter(KnownUser.pseudo == pseudo).first()
            if user:
                return user
        jid = bot.occupants.pseudo_to_jid(pseudo)
        if jid:
            usersjid = bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == jid).first()
            if usersjid:
                return usersjid.user
        return None

    @staticmethod
    def get_antihl(pseudo, bot):
        user = KnownUser.get(pseudo, bot, authviapseudo=True)
        if user:
            return user.get_pseudo()
        return pseudo

    @staticmethod
    def get_all(bot, separator, exceptions=[]):
        return separator.join([KnownUser.get_antihl(user.nickname, bot) for user in bot.occupants.users.values()
            if user.nickname not in exceptions])


class KnownUsersJIDs(Base):
    __tablename__ = "knownusersjids"
    jid = Column(String(250), primary_key=True)
    users_kuid = Column(Integer, ForeignKey('knownuser.kuid'))
    user = relationship(KnownUser, primaryjoin=users_kuid == KnownUser.kuid)

    def __init__(self, jid, kuid):
        self.jid = jid
        self.users_kuid = kuid


class Chans(Base):
    __tablename__ = "chans"
    cid = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)

    def __init__(self, name):
        self.name = name


class KnownUsersManager(SyncModule):
    def __init__(self, bot):
        desc = _("user: shows this help")
        desc += _("\nuser register <args>: register user <pseudo> (defaults: you) with JID(s) <jid(s)> (defaults: your JID)")
        desc += _("\nuser show: prints the whole Knows Users database")
        desc += _("\nuser show <pseudo>: prints informations about <pseudo> (can also be 'me')")
        desc += _("\nuser permlvl [<pseudo>]: prints the Permission Level of <pseudo> (defaults: you)")
        desc += _("\nuser permlvl [<pseudo>] <lvl>: sets the Permission Level of <pseudo> (defaults: you) to <lvl>")
        desc += _("\nuser nick <pseudo>: sets your pseudo to <pseudo>")
        desc += _("\nuser antihl <hl_pseudo>: sets your antihl-pseudo to <hl_pseudo>")
        desc += _("\nuser del <jid>: deletes <jid>")
        desc += _("\nuser add: show the connected user you can add")
        SyncModule.__init__(self,
                bot,
                desc=desc,
                name="user")
        self.logger = logging.getLogger("pipobot.knownusers")

        try:
            for admin in self._settings["admins"]:
                user = ''
                if '@' in admin:
                    usersjid = bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == admin).first()
                    if usersjid:
                        user = usersjid.user
                    else:
                        self.logger.error(_('Admin %s is not yet registered !' % admin))
                else:
                    user = bot.session.query(KnownUser).filter(KnownUser.pseudo == admin).first()
                if user:
                    user.permlvl = 5
                    bot.session.commit()
                else:
                    self.logger.error(_('Admin %s is not yet registered !' % admin))
        except KeyError:
            self.logger.error(_('You shall add an admin section in your configuration file'))

    @answercmd('add')
    def answer_add(self, sender):
        unknown_users = [u for u in self.bot.occupants.users.values() if KnownUser.get(u.jid, self.bot) is None and u.nickname != self.bot.name]
        if unknown_users:
            return _("I don't know: ") + ', '.join(['%s (%s)' % (u.nickname, u.jid) for u in unknown_users])
        return _("I know everybody here !")

    @answercmd('del (?P<jid>.*)')
    def answer_del(self, sender, jid):
        senderuser = KnownUser.get(sender, self.bot, authviapseudo=False)
        if not senderuser:
            return _("I don't know you, %s" % sender)
        jid = self.bot.session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid == jid).first()
        if not jid:
            return _("I don't know this JID...")
        if not senderuser.has_the_power_on(jid.user, self.bot.chatname):
            return _("You have no power here, %s the Grey!" % senderuser.get_pseudo())
        self.bot.session.delete(jid)
        self.bot.session.commit()
        return _("%s as been deleted" % jid.jid)

    @answercmd('register', r'register (?P<pseudo>\S+)(?P<jids>.*)')
    def answer_register(self, sender, pseudo="", jids=""):
        if '@' in pseudo:
            jids = pseudo + jids
            pseudo = sender
        if not pseudo:
            pseudo = sender
        if not jids:
            jids = [self.bot.occupants.pseudo_to_jid(pseudo)]
        else:
            jids = jids.split()

        senderuser = KnownUser.get(sender, self.bot, authviapseudo=False)
        if pseudo != sender:
            if not senderuser:
                return _("I don't know you %s…" % sender)
            if senderuser.get_permlvl(self.bot.chatname) < 2:
                return _("I don't trust you, %s…" % sender)

        targetuser = None
        newtargetuser = False
        if pseudo or not senderuser:
            targetuser = KnownUser.get(pseudo, self.bot, authviapseudo=True)
            if not targetuser:
                newtargetuser = True
                targetuser = KnownUser(pseudo=pseudo)
                self.bot.session.add(targetuser)
                self.bot.session.commit()
                targetuser = KnownUser.get(pseudo, self.bot, authviapseudo=True)
            elif not senderuser.has_the_power_on(targetuser, self.bot.chatname):
                return _("%s: %s is already registered, and you can't modify his settings" % (senderuser.pseudo, targetuser.pseudo))
        else:
            targetuser = senderuser

        for jid in jids:
            check = KnownUser.get(jid, self.bot, authviapseudo=False)
            if check:
                ret = _("%s: %s is associated to JID(s) " % (sender, check.pseudo))
                for jid in check.jids:
                    ret += '%s ' % jid.jid
                if newtargetuser:
                    self.bot.session.delete(targetuser)
                    self.bot.session.commit()
                return ret
            if jid:
                j = KnownUsersJIDs(jid, targetuser.kuid)
                self.bot.session.add(j)
        self.bot.session.commit()

        return _("pseudo %s is now associated to jid(s) %s" % (pseudo, jids))

    def show_all_users(self):
        ret = _('Registered users:')
        users = self.bot.session.query(KnownUser).all()
        for user in users:
            ret += "\n  %-30s %s " % (user.pseudo, user.permlvl)
            for jid in user.jids:
                ret += '%s ' % jid.jid
            if user.chanperms:
                ret += _("\n    special permissions: %s" % user.chanperms)
        return ret

    def show_one_user(self, user, authviapseudo=True):
        knownuser = KnownUser.get(user, self.bot, authviapseudo=authviapseudo)
        if not knownuser:
            return _("I don't know that %s…" % user)
        ret = knownuser.get_pseudo(hl=True)
        if knownuser.hl_pseudo is not None:
            ret += ' (%s)' % knownuser.hl_pseudo
        ret += _(': Your Permission Level is %s, and your JID(s) are:' % knownuser.permlvl)
        for jid in knownuser.jids:
            ret += ' %s' % jid.jid
        return ret

    @answercmd('show', r'show (?P<user>\S+)')
    def answer_show(self, sender, user=""):
        authviapseudo = True
        if user == "me":
            user = sender
            authviapseudo = False
        return self.show_one_user(user, authviapseudo) if user else self.show_all_users()

    @answercmd(r'permlvl (?P<pseudo>\S+) (?P<lvl>\d+)')
    def answer_permlvl(self, sender, pseudo="", lvl=0):
        if not pseudo:
            pseudo = sender
        user = KnownUser.get(pseudo, self.bot, authviapseudo=True)
        if not user:
            return _("I don't know you, %s…" % sender)
        if not lvl:
            ret = _('%s: Your Permission Level is %i' % (user.pseudo, user.permlvl))
            if user.chanperms:
                ret += _(", and you have specials rights on some chans: %s" % user.chanperms)
            return ret

        user = KnownUser.get(pseudo, self.bot, authviapseudo=False)
        if not user:
            return _("%s: I don't trust you…" % sender)

        senderuser = KnownUser.get(sender, self.bot, authviapseudo=False)
        if not senderuser:
            return _("I don't know you, %s…" % sender)

        if not senderuser.has_the_power_on(user, self.bot.chatname):
            return _("%s: you don't have the right permissons to do that." % sender)
        if lvl > senderuser.permlvl:
            return _("%s: No, you can't give more rights than you have…" % sender)

        if lvl == 2 or lvl == 4:
            chan = self.bot.session.query(Chans).filter(Chans.name == self.bot.chatname).first()
            if not chan:
                chan = Chans(self.bot.chatname)
                self.bot.session.add(chan)
                self.bot.session.commit()
                chan = self.bot.session.query(Chans).filter(Chans.name == self.bot.chatname).first()
            for chanperm in user.chanperms:
                if chanperm.chans_cid == chan.cid:
                    chanperm.permlvl = lvl
                    break
            else:
                perchanperm = PerChanPermissions(lvl)
                perchanperm.chan = chan
                self.bot.session.add(perchanperm)
                user.chanperms.append(perchanperm)
        else:
            user.permlvl = lvl
        self.bot.session.commit()

        return _("%s's Permission Level modified to %i" % (pseudo, lvl))

    @answercmd(r'nick (?P<nickname>\S+)')
    def answer_nick(self, sender, nickname):
        senderuser = KnownUser.get(sender, self.bot, authviapseudo=False)
        if not senderuser:
            return _("I don't know you, %s…" % sender)
        try:
            senderuser.pseudo = nickname
            self.bot.session.commit()
            return _("%s: your pseudo is now %s" % (sender, senderuser.pseudo))
        except IntegrityError:
            self.bot.session.rollback()
            return _("%s: DO NOT EVEN *THINK* ABOUT DOING THAT" % sender)

    @answercmd(r'antihl (?P<nickname>\S+)')
    def answer_hl(self, sender, nickname):
        senderuser = KnownUser.get(sender, self.bot, authviapseudo=False)
        if not senderuser:
            return _("I don't know you, %s…" % sender)
        senderuser.hl_pseudo = nickname
        self.bot.session.commit()
        return _("%s: your highlight-pseudo is now %s" % (sender, senderuser.hl_pseudo))

    @defaultcmd
    def answer(self, sender, args):
        return self.desc
