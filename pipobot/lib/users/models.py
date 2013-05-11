from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pipobot.lib.bdd import Base


class KnownUser(Base):
    __tablename__ = "knownuser"
    uid = Column(Integer, primary_key=True)
    jids = relationship("KnownUsersJIDs")
    chans = relationship("ChanParticipant")

    def __init__(self):
        self.chans = []

    def __str__(self):
        return "uid %s, jids %s, chans %s" % (self.uid, self.jids, self.chans)

    def list_jids(self):
        return [jid.jid for jid in self.jids]

    def print_jids(self):
        return ",".join(self.list_jids())

    def __contains__(self, data):
        if isinstance(data, KnownUsersJIDs):
            return data in self.jids
        elif isinstance(data, (str, unicode)):
            return data in [jid.jid for jid in self.jids]


class Chan(Base):
    __tablename__ = "chans"
    jid = Column(String(250), primary_key=True)
    participants = relationship("ChanParticipant")
    groups = relationship("ChanGroup")

    def __init__(self, chan_name):
        self.jid = chan_name

    def __contains__(self, data):
        if isinstance(data, KnownUser):
            return any(usr.user == data for usr in self.participants)
        elif isinstance(data, (str, unicode)):
            return any(user.nickname == data for user in self.participants)


class ChanParticipant(Base):
    __tablename__ = "chanparticipant"
    chan_id = Column(String(250), ForeignKey("chans.jid"), primary_key=True)
    chan = relationship(Chan, primaryjoin=Chan.jid == chan_id)
    knownuser_uid = Column(Integer, ForeignKey("knownuser.uid"), primary_key=True)
    nickname = Column(String(50))
    user = relationship(KnownUser, primaryjoin=knownuser_uid == KnownUser.uid)

    __table_args__ = (UniqueConstraint('chan_id', 'nickname', name='chan_nickname'),)

    def __init__(self, chan, nickname):
        self.chan_id = chan
        self.nickname = nickname

    def __str__(self):
        return "Nickname is %s and jids are %s" % (self.nickname, ",".join(str(jid) for jid in self.user.jids))

    def list_jids(self):
        return [jid.jid for jid in self.user.jids]

    def print_jids(self):
        return ",".join(self.list_jids())

    def __contains__(self, jid):
        """ Checks if the corresponding KnownUser contains this jid """
        return jid in self.user


class ChanGroup(Base):
    __tablename__ = "changroup"
    chan_id = Column(String(250), ForeignKey("chans.jid"), primary_key=True)
    groupname = Column(String(50))
    chan = relationship(Chan, primaryjoin=Chan.jid == chan_id)
    members = relationship("GroupMember")
    __table_args__ = (UniqueConstraint('chan_id', 'groupname', name='chan_groupname'),)

    def __init__(self, chan_id, groupname):
        self.chan_id = chan_id
        self.groupname = groupname

    def __contains__(self, user):
        if isinstance(user, GroupMember):
            return user in self.members
        elif isinstance(user, KnownUser):
            return any(user == member.user for member in self.members)
        elif isinstance(user, ChanParticipant):
            return user.user in self
        elif isinstance(user, (str, unicode)):
            return any(any(chan.nickname == user for chan in member.user.chans) for member in self.members)


class GroupMember(Base):
    __tablename__ = "chan_group_association"
    knownuser_uid = Column(Integer, ForeignKey('knownuser.uid'), primary_key=True)
    changroup_groupname = Column(String(50), ForeignKey("changroup.groupname"))
    admin = Column(Boolean)
    moderator = Column(Boolean)
    user = relationship(KnownUser, primaryjoin=KnownUser.uid == knownuser_uid)
    group = relationship(ChanGroup, primaryjoin=ChanGroup.groupname == changroup_groupname)

    def __init__(self, user, group, admin=False, moderator=False):
        self.user = user
        self.group = group
        self.admin = admin
        self.moderator = moderator


class KnownUsersJIDs(Base):
    __tablename__ = "knownusersjids"
    jid = Column(String(250), primary_key=True)
    users_kuid = Column(Integer, ForeignKey('knownuser.uid'))
    user = relationship(KnownUser, primaryjoin=users_kuid == KnownUser.uid)

    def __init__(self, jid):
        self.jid = jid

    def __str__(self):
        return self.jid

