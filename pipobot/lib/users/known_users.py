import logging
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from pipobot.lib.bdd import Base


logger = logging.getLogger("pipobot.lib.users.known_users")


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


class KnownUserManager(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def safe_commit(self, obj, error_msg):
        try:
            self.db_session.commit()
        except (IntegrityError, FlushError):
            logger.info(error_msg)
            self.db_session.rollback()
            return None
        return obj

    def create_chan(self, chan_name):
        chan = Chan(chan_name)
        self.db_session.add(chan)
        commit = self.safe_commit(chan, "Try to create an already existing chan %s" % chan_name)
        return commit

    def create_known_user(self, jids=[]):
        user = KnownUser()
        self.db_session.add(user)
        ret = self.add_jids_to_user(user, jids)
        if ret is None:
            return ret
        return user

    def get_known_user(self, pseudo, chan):
        user = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                             ChanParticipant.nickname==pseudo).first()
        if user is None:
            logger.info("No KnownUser with pseudo %s", pseudo)
        return user

    def add_jids_to_user(self, user, jids=[]):
        for jid in jids:
            new_jid = KnownUsersJIDs(jid)
            user.jids.append(new_jid)
            self.db_session.add(new_jid)
            commit = self.safe_commit(user, "")
            if commit is None:
                return None
        return user

    def set_nickname(self, user_jid, chan, nickname):
        jid = self.db_session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid==user_jid).first()
        if jid is not None:
            user = jid.user
            assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                  ChanParticipant.knownuser_uid==user.uid).first()
            if assoc is not None:
                assoc.nickname = nickname
                self.safe_commit(assoc, "")
            else:
                assoc = ChanParticipant(chan, nickname)
                assoc.user = user
                user.chans.append(assoc)
                self.db_session.add(assoc)
                self.safe_commit([assoc, user], "An user already have the nickname %s in the room %s !" % (nickname, chan))
            return user

    def change_nickname(self, old_pseudo, new_pseudo, chan):
        assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                              ChanParticipant.nickname==old_pseudo).first()
        if assoc is not None:
            assoc.nickname = new_pseudo
            assoc = self.safe_commit(assoc, "Try to use an already existing pseudo : %s" % new_pseudo)
        return assoc

    def create_group(self, groupname, chan):
        group = ChanGroup(chan, groupname)
        self.db_session.add(group)
        self.safe_commit(group, "The group %s already exists in %s" % (groupname, chan))
        return group

    def get_group(self, groupname, chan):
        group = self.db_session.query(ChanGroup).filter(ChanGroup.groupname == groupname,
                                                        ChanGroup.chan_id == chan).first()
        if group is None:
            logger.info("No group named %s in the chan %s", groupname, chan)
            return None
        return group

    def add_user_to_group(self, groupname, chan, user):
        group = self.db_session.query(ChanGroup).filter(ChanGroup.groupname == groupname,
                                                        ChanGroup.chan_id == chan).first()
        assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                              ChanParticipant.nickname==user).first()
        group.members.append(assoc.user)
        return group
