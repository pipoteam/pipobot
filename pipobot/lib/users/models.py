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

class Chan(Base):
    __tablename__ = "chans"
    jid = Column(String(250), primary_key=True)

    def __init__(self, chan_name):
        self.jid = chan_name


class ChanParticipant(Base):
    __tablename__ = "chanparticipant"
    chan_id = Column(String(250), ForeignKey("chans.jid"), primary_key=True)
    knownuser_uid = Column(Integer, ForeignKey("knownuser.uid"), primary_key=True)
    nickname = Column(String(50))
    user = relationship(KnownUser, primaryjoin=knownuser_uid == KnownUser.uid)

    __table_args__ = (UniqueConstraint('chan_id', 'nickname', name='chan_nickname'),)

    def __init__(self, chan_id, nickname):
        self.chan_id = chan_id
        self.nickname = nickname

    def __str__(self):
        return "Nickname is %s and jids are %s" % (self.nickname, ",".join(str(jid) for jid in self.user.jids))

    def list_jids(self):
        return [jid.jid for jid in self.user.jids]

    def print_jids(self):
        return ",".join(self.list_jids())


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

