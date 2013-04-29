import logging
import traceback
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from pipobot.lib.users.models import *


logger = logging.getLogger("pipobot.lib.users.known_users")


class KnownUserManager(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def safe_commit(self, obj, error_msg):
        try:
            self.db_session.commit()
        except (IntegrityError, FlushError):
            print traceback.format_exc()
            logger.debug(traceback.format_exc().decode("utf-8"))
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
        ret = self._add_jids_to_user(user, jids)
        if ret is None:
            return ret
        return user

    def get_assoc_user(self, pseudo, chan):
        particip = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                 ChanParticipant.nickname==pseudo).first()
        return particip

    def get_known_user(self, pseudo=None, chan=None, jid=None):
        if chan is not None and pseudo is not None:
            particip = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                     ChanParticipant.nickname==pseudo).first()
            if particip is None:
                logger.info("No KnownUser with pseudo %s on chan %s", pseudo, chan)
            else:
                user = particip.user
        elif jid is not None:
            knownjid = self.db_session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid==jid).first()
            user = knownjid.user if knownjid is not None else None
            if user is None:
                logger.info("No KnownUser with jid %s", jid)
        else:
            logger.info("You must provide (pseudo, chan) or (jid) to search for a Known User")
            return None

        return user

    def _add_jids_to_user(self, user, jids=[]):
        for jid in jids:
            new_jid = KnownUsersJIDs(jid)
            user.jids.append(new_jid)
            self.db_session.add(new_jid)
            commit = self.safe_commit(user, "")
            if commit is None:
                return None
        return user

    def remove_known_user(self, pseudo=None, chan=None, jid=None):
        user = self.get_known_user(pseudo=pseudo, chan=chan, jid=jid)
        if user is None:
            logger.info("Can't find a user with jid %s", jid)
        else:
            for jid in user.jids:
                self.db_session.delete(jid)
            # Remove each subscriptions of the user to chans
            for chan in user.chans:
                self.db_session.delete(chan)
            # Remove the user
            self.db_session.delete(user)
            self.db_session.commit()
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
        assoc = self.get_assoc_user(old_pseudo, chan)
        if assoc is not None:
            assoc.nickname = new_pseudo
            assoc = self.safe_commit(assoc, "Try to use an already existing pseudo : %s" % new_pseudo)
        return assoc

    def remove_nickname(self, pseudo=None, chan=None, jid=None):
        if chan is not None:
            logger.error("You must provide a chan to remove a nickname from a chan")
        else:
            if pseudo is None and jid is None:
                logger.error("You must provide either a jid or a pseudo to remove a nickname from a chan")
                return

            if pseudo is not None:
                assoc = self.get_assoc_user(pseudo=pseudo, chan=chan)
            elif jid is not None:
                user = self.get_known_user(jid=jid)
                if user is None:
                    return None
                assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                      ChanParticipant.knownuser_uid==user.uid).first()

            if assoc is not None:
                self.db_session.delete(assoc)
                self.db_session.commit()
            else:
                logger.error("Can't find a user registerd with pseudo %s in chan %s with jid %s", pseudo, chan, jid)
                return None

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
        self.db_session.commit()
        return group

    def remove_user_from_group(self, groupname, chan, nickname):
        group = self.get_group(groupname, chan)
        if group is None:
            log.error("The group %s does not exist on chan %s so it can't be removed !", groupname, chan)
            return group

        user = self.get_known_user(pseudo=nickname, chan=chan)
        if user is None:
            log.error("The user %s does not exist in chan %s so can't be removed from the group %s", nickname, chan, groupname)
            return None

        if user in group.members:
            group.members.remove(user)
            self.db_session.commit()
            return user
        else:
            log.error("User %s not in group %s for chan %s : nothing to remove !", nickname, groupname, chan)
            return None

    def remove_group(self, groupname, chan):
        group = self.get_group(groupname, chan)
        if group is None:
            return None
        self.db_session.delete(group)
        self.db_session.commit()
        return group
