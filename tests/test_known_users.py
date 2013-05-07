from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest

from pipobot.lib.bdd import Base
from pipobot.lib.users.known_users import KnownUserManager
from pipobot.lib.users.exceptions import *

TEST_CHAN = "test@chan.domain.tld"


class TestKnownUser(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        self.manager = KnownUserManager(session)

    def add_known_user(self, chan, jid, nickname):
        # Create a room
        try:
            chan = self.manager.create_chan(chan)
        except ChanConflict:
            pass

        # Add a KnownUser
        usr = self.manager.create_known_user([jid])
        self.assertIsNotNone(usr)

        # Add the user to the room with nickname 'pouet'
        ret = self.manager.set_nickname(jid, TEST_CHAN, nickname)
        self.assertEqual(ret.chans[0].nickname, nickname)
        self.assertEqual(ret, usr)
        return usr, chan

    def test_add_knownuser(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Get a KnownUser
        assoc = self.manager.get_assoc_user(pseudo="pouet", chan=TEST_CHAN)
        self.assertEqual(assoc.nickname, "pouet")

        # Add a KnownUser that already exists : returns None and does nothing
        self.assertRaises(JIDConflict, callable=self.manager.create_known_user, args=(["pouet@domain.tld"]))

        pouet, chan = self.add_known_user(TEST_CHAN, "pipo@domain.tld", "pipo")
        self.assertRaises(NicknameConflict, callable=self.manager.set_nickname, args=("pipo@domain.tld", TEST_CHAN, "pouet"))

        self.assertRaises(JIDConflict, callable=self.add_known_user, args=(TEST_CHAN, "pouet@domain.tld", "qsdf"))

    def test_remove_knownuser(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Try to remove the user pouet by jid
        ret = self.manager.remove_known_user(jid="pouet@domain.tld")
        self.assertEqual(ret, pouet)

        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Try to remove the user pouet by nickname/chan
        ret = self.manager.remove_known_user(pseudo="pouet", chan=TEST_CHAN)
        self.assertEqual(ret, pouet)


    def test_change_nick(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")
        pipo, chan = self.add_known_user(TEST_CHAN, "pipo@domain.tld", "pipo")

        # Change the nickname of "pouet" to "plop"
        self.manager.change_nickname("pouet", "plop", TEST_CHAN)
        # Check that the user known as "plop" is the same has "pouet" used to be
        plop = self.manager.get_assoc_user(pseudo="plop", chan=TEST_CHAN)
        self.assertEqual(plop.user, pouet)

        # Try to change the nickname of a user who does not exist : raises an exception
        self.assertRaises(NoKnownUser, callable=self.manager.change_nickname, args=("unknown", "pipo", TEST_CHAN))

        # Try to use a new nickname that already exists : nothing happens, "plop" is still "plop"
        self.assertRaises(NicknameConflict, callable=self.manager.change_nickname, args=("plop", "pipo", TEST_CHAN))

    def test_group(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Create a group
        group = self.manager.create_group("admin", TEST_CHAN)
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)

        self.assertRaises(GroupConflict, callable=self.manager.create_group, args=("admin", TEST_CHAN))

        # Add the user to the group
        group = self.manager.add_user_to_group("admin", TEST_CHAN, "pouet")
        # Check that we modified the appropriate group
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)
        # Check that the user were correctly added to the group
        self.assertEqual(group.members[0].user, pouet)

        # Try to add twice the same user to the group
        self.assertRaises(GroupMemberConflict, callable=self.manager.add_user_to_group, args=("admin", TEST_CHAN, "pouet"))

        # Try to retrieve a group
        admin = self.manager.get_group("admin", TEST_CHAN)
        # Check that we got the appropriate group
        self.assertEqual(admin.groupname, "admin")
        self.assertEqual(admin.chan, chan)
        # Check that the user is still in the group
        self.assertEqual(admin.members[0].user, pouet)

        # Try to retrieve a non-existing group
        self.assertRaises(NoGroupFound, callable=self.manager.get_group, args=("pipo", TEST_CHAN))

        # Add a second user to the group
        pipo, chan = self.add_known_user(TEST_CHAN, "pipo@domain.tld", "pipo")
        group = self.manager.add_user_to_group("admin", TEST_CHAN, "pipo")
        # The group now contains pipo and pouet
        self.assertEqual(len(group.members), 2)
        self.assertEqual(group.members[0].user, pouet)
        self.assertEqual(group.members[1].user, pipo)

        # Remove an user from the group
        user = self.manager.remove_user_from_group("admin", TEST_CHAN, "pipo")
        self.assertEqual(user, pipo)

        # Remove a user from a group that does not exist
        self.assertRaises(NoGroupFound, callable=self.manager.remove_user_from_group, args=("unknown", TEST_CHAN, "whatever"))

        # Retrieve the group and check that it contains only pouet
        admin = self.manager.get_group("admin", TEST_CHAN)
        self.assertEqual(len(group.members), 1)
        self.assertEqual(group.members[0].user, pouet)

        # Remove a group
        group = self.manager.remove_group("admin", TEST_CHAN)
        self.assertEqual(group, admin)

        # Check that the group was removed
        self.assertRaises(NoGroupFound, callable=self.manager.get_group, args=("pipo", TEST_CHAN))

    def test_group_permission(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Create a group
        group = self.manager.create_group("pipoteam", TEST_CHAN)
        self.assertEqual(group.groupname, "pipoteam")
        self.assertEqual(group.chan, chan)

        # Add the user to the group
        group = self.manager.add_user_to_group("pipoteam", TEST_CHAN, "pouet")
        # Check that we modified the appropriate group
        self.assertEqual(group.groupname, "pipoteam")
        self.assertEqual(group.chan, chan)
        # Check that the user were correctly added to the group
        self.assertEqual(group.members[0].user, pouet)

        # pouet is not yet admin
        self.assertFalse(group.members[0].admin)
        self.assertFalse(group.members[0].moderator)

        member = self.manager.set_permission("pipoteam", "pouet", TEST_CHAN, admin=True, moderator=False)

        # pouet is admin and not moderator
        self.assertEqual(group.members[0], member)
        self.assertTrue(group.members[0].admin)
        self.assertFalse(group.members[0].moderator)

        member = self.manager.set_permission("pipoteam", "pouet", TEST_CHAN, moderator=True)
        self.assertEqual(group.members[0], member)
        self.assertTrue(group.members[0].moderator)
