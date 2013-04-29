from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy import Table, Column, String, Integer, ForeignKey
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


chan_group_association = Table("chan_group_association", Base.metadata,
                        Column("knownuser_uid", Integer, ForeignKey('knownuser.uid')),
                        Column("changroup_groupname", String(50), ForeignKey("changroup.groupname")))


class ChanGroup(Base):
    __tablename__ = "changroup"
    chan_id = Column(String(250), ForeignKey("chans.jid"), primary_key=True)
    groupname = Column(String(50))
    chan = relationship(Chan, primaryjoin=Chan.jid == chan_id)
    members = relationship("KnownUser", secondary=chan_group_association)
    __table_args__ = (UniqueConstraint('chan_id', 'groupname', name='chan_groupname'),)

    def __init__(self, chan_id, groupname):
        self.chan_id = chan_id
        self.groupname = groupname


class KnownUsersJIDs(Base):
    __tablename__ = "knownusersjids"
    jid = Column(String(250), primary_key=True)
    users_kuid = Column(Integer, ForeignKey('knownuser.uid'))
    user = relationship(KnownUser, primaryjoin=users_kuid == KnownUser.uid)

    def __init__(self, jid):
        self.jid = jid

    def __str__(self):
        return self.jid

