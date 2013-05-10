import logging
import traceback
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError, NoResultFound
from pipobot.lib.users.models import *
from pipobot.lib.users.exceptions import *


logger = logging.getLogger("pipobot.lib.users.known_users")


class KnownUserManager(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def safe_commit(self, exc, error_msg):
        try:
            self.db_session.commit()
        except (IntegrityError, FlushError):
            print traceback.format_exc()
            self.db_session.rollback()
            raise exc(*error_msg)

    #############################################################################################
    #           CREATION METHODS                                                                #
    #############################################################################################

    def _add_jids_to_user(self, user, jids=[]):
        """ Creation of a JID to be associated to a KnownUser

            :param user: the user we add jids to
            :param jids: a list of jids
            :type user: KnownUser
            :type jids: str list
            :rtype: KnownUser
            :raises: :class:`pipobot.lib.users.exceptions.JIDConflict`
        """

        for jid in jids:
            new_jid = KnownUsersJIDs(jid)
            user.jids.append(new_jid)
            self.db_session.add(new_jid)
            commit = self.safe_commit(JIDConflict, jid)
        return user

    def create_chan(self, chan_name):
        """ Creation of a Chan

            :param chan_name: The jid of the chan we create
            :rtype: Chan
            :raises: :exc:`ChanConflict`
        """
        chan = Chan(chan_name)
        self.db_session.add(chan)
        self.safe_commit(ChanConflict, chan_name)
        return chan

    def create_known_user(self, jids=[]):
        """ Creation of a KnownUser

            :param jids: JIDs of the user
            :type jids: str list
            :rtype: :class:`pipobot.lib.users.exceptions.KnownUser`
            :raises: :exc:`JIDConflict`
        """

        user = KnownUser()
        self.db_session.add(user)
        addjid_success = self._add_jids_to_user(user, jids)
        return user

    def create_group(self, groupname, chan):
        """ Creation of a ChanGroup

            :param groupname: The name of the group
            :param chan: The name of the chan we create the group in
            :rtype: :class:`pipobot.lib.users.exceptions.ChanGroup`
            :raises: :exc:`GroupConflict`
        """

        group = ChanGroup(chan, groupname)
        self.db_session.add(group)
        self.safe_commit(GroupConflict, [groupname, chan])
        return group

    def set_nickname(self, user_jid, chan, nickname):
        """ Creation of a ChanParticipant : association of a chan and a user, with a nickname

            :param user_jid: The jid of the user we want to associate to a chan
            :param chan: The name of the chan
            :param nickname: The nickname of the user in the chan
            :rtype: KnownUser
            :raises: NoKnownUser, NicknameConflict
        """

        jid = self.db_session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid==user_jid).first()
        if jid is not None:
            user = jid.user
        else:
            raise NoKnownUser(jid=user_jid)

        try:
            assoc = self.get_assoc_user(chan=chan, jid=user_jid)
            assoc.nickname = nickname
        except NoKnownUser:
            assoc = ChanParticipant(chan, nickname)
            assoc.user = user
            user.chans.append(assoc)
            self.db_session.add(assoc)

        self.safe_commit(NicknameConflict, [nickname, chan])
        return user

    def add_user_to_group(self, groupname, chan, pseudo):
        """ Creation of a GroupMember : a user is associated to a group in a chan

            :param groupname: Name of the group to add the user in
            :param chan: Name of the chan in which we search the group and the user
            :param pseudo: Pseudo of the user in the chan
            :rtype: ChanGroup
            :raises: NoGroupFound, RequestError, NoKnownUser"""
        group = self.get_group(groupname, chan)
        assoc = self.get_assoc_user(pseudo=pseudo, chan=chan)

        changroup = GroupMember(assoc.user, group)
        group.members.append(changroup)
        self.safe_commit(GroupMemberConflict, [groupname, chan, pseudo])
        return group


    #############################################################################################
    #           GETTER METHODS                                                                  #
    #############################################################################################

    def get_known_user(self, pseudo=None, chan=None, jid=None):
        """ Retrieve a KnownUser with either a jid, or a (pseudo, chan)

            :param pseudo: Nickname of the user in a chan
            :param chan: JID of the chan
            :param jid: JID of a user to search
            :raises: RequestError, NoKnownUser
        """
        user = None
        if chan is not None and pseudo is not None:
            assoc = self.get_assoc_user(pseudo=pseudo, chan=chan)
            user = assoc.user
        elif jid is not None:
            try:
                knownjid = self.db_session.query(KnownUsersJIDs).filter(KnownUsersJIDs.jid==jid).one()
                user = knownjid.user
            except NoResultFound:
                raise NoKnownUser(jid=jid)
        else:
            raise RequestError("You must provide (pseudo, chan) or (jid) to search for a Known User")

        return user

    def get_group(self, groupname, chan):
        """ Retrieve a group within a chan

            :param groupname: The name of the group to search
            :param chan: The JID of the chan
            :raises: NoGroupFound
        """
        try:
            group = self.db_session.query(ChanGroup).filter(ChanGroup.groupname == groupname,
                                                            ChanGroup.chan_id == chan).one()
        except NoResultFound:
            raise NoGroupFound(groupname, chan)
        return group

    def get_assoc_user(self, pseudo=None, chan=None, jid=None):
        """ Retrieve a ChanParticipant (association of a user and a chan) with (jid, chan) or (pseudo, chan)

            :param pseudo: Nickname of the user in a chan
            :param chan: JID of the chan
            :param jid: JID of a user to search
            :raises: RequestError, NoKnownUser
        """
        if pseudo is not None and chan is not None:
            assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                     ChanParticipant.nickname==pseudo).first()
        elif jid is not None and chan is not None:
            user = self.get_known_user(jid=jid)
            assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan,
                                                                  ChanParticipant.knownuser_uid==user.uid).first()
        else:
            raise RequestError("You must provide (pseudo, chan) or (jid, chan) to search for a Known User")

        if assoc is None:
            raise NoKnownUser(pseudo=pseudo, chan=chan)
        return assoc

    def get_all_users(self, chan):
        assoc = self.db_session.query(ChanParticipant).filter(ChanParticipant.chan_id==chan).all()
        return assoc

    #############################################################################################
    #      METHODS TO UPDATE DATA                                                               #
    #############################################################################################

    def change_nickname(self, old_pseudo, new_pseudo, chan):
        """ Change the nickname of a user in a chan

            :param old_pseudo: The old nickname
            :param new_pseudo: The new nickname
            :param chan: The JID of the chan
            :raises: NicknameConflict, NoKnownUser
        """
        assoc = self.get_assoc_user(pseudo=old_pseudo, chan=chan)
        assoc.nickname = new_pseudo
        assoc = self.safe_commit(NicknameConflict, [new_pseudo, chan])
        return assoc

    def set_permission(self, groupname, user, chan, admin=None, moderator=None):
        """ Set the admin/moderator permission of a user in a group

            :param groupname: The name of the group
            :param user: The user to modify
            :param chan: The chan containing the group
            :param admin: To set the 'admin' permission
            :type admin: boolean
            :param moderator: To set the 'moderator' permission
            :type moderator: boolean
            :raises: GroupMemberError
        """
        try:
            member = self.db_session.query(GroupMember).filter(ChanGroup.groupname==groupname,
                                                               ChanGroup.chan_id==chan,
                                                               ChanParticipant.nickname==user).one()
        except:
            raise GroupMemberError(groupname, chan, user)

        if admin is not None:
            member.admin = admin

        if moderator is not None:
            member.moderator = moderator

        self.db_session.commit()
        return member

    #############################################################################################
    #        METHODS TO REMOVE DATA                                                             #
    #############################################################################################

    def remove_known_user(self, pseudo=None, chan=None, jid=None):
        """ Remove a KnownUser from the database with either (pseudo, chan) or jid

            :param pseudo: The nickname of the user to remove
            :param chan: The chan to find the user
            :param jid: The jid of the user
            :raises: NoKnownUser
        """
        user = self.get_known_user(pseudo=pseudo, chan=chan, jid=jid)
        if user is None:
            raise NoKnownUser(jid=jid)
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

    def remove_group(self, groupname, chan):
        """ Remove a ChanGroup with

            :param groupname: The name of the group
            :param chan: The chan containing the group
            :raises: NoGroupFound
        """
        group = self.get_group(groupname, chan)
        self.db_session.delete(group)
        self.db_session.commit()
        return group

    def remove_nickname(self, pseudo=None, chan=None, jid=None):
        """ Remove a ChanParticipant (association of a user and a chan)

            :param pseudo: Nickname of the user in a chan
            :param chan: JID of the chan
            :param jid: JID of a user to search
            :raises: RequestError, NoKnownUser
        """
        if chan is None:
            raise RequestError("You must provide a chan to remove a nickname from a chan")
        else:
            assoc = self.get_assoc_user(pseudo=pseudo, chan=chan, jid=jid)
            self.db_session.delete(assoc)
            self.db_session.commit()

    def remove_user_from_group(self, groupname, chan, nickname):
        """ Remove a user from a group

            :param groupname: The name of the group
            :param chan: The chan
            :param nickname: The nickname of the user
            :raises: GroupMemberError, NoGroupFound, NoKnownUser
        """
        group = self.get_group(groupname, chan)
        user = self.get_known_user(pseudo=nickname, chan=chan)

        for member in group.members:
            if member.user == user:
                group.members.remove(member)
                self.db_session.commit()
                return user
        else:
            raise GroupMemberError(groupname, chan, nickname)
