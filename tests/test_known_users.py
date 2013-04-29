from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest

from pipobot.lib.bdd import Base
from pipobot.lib.users.known_users import KnownUserManager

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
        chan = self.manager.create_chan(chan)

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
        add = self.manager.create_known_user(["pouet@domain.tld"])
        self.assertIsNone(add)

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

        # Try to change the nickname of a user who does not exist : return None and do nothing
        ret = self.manager.change_nickname("unknown", "pipo", TEST_CHAN)
        self.assertIsNone(ret)

        # Try to use a new nickname that already exists : nothing happens, "plop" is still "plop"
        ret = self.manager.change_nickname("plop", "pipo", TEST_CHAN)
        self.assertEqual(plop.nickname, "plop")
        self.assertIsNone(ret)

    def test_group(self):
        pouet, chan = self.add_known_user(TEST_CHAN, "pouet@domain.tld", "pouet")

        # Create a group
        group = self.manager.create_group("admin", TEST_CHAN)
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)

        # Add the user to the group
        group = self.manager.add_user_to_group("admin", TEST_CHAN, "pouet")
        # Check that we modified the appropriate group
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)
        # Check that the user were correctly added to the group
        self.assertEqual(group.members[0], pouet)

        # Try to retrieve a group
        admin = self.manager.get_group("admin", TEST_CHAN)
        # Check that we got the appropriate group
        self.assertEqual(admin.groupname, "admin")
        self.assertEqual(admin.chan, chan)
        # Check that the user is still in the group
        self.assertEqual(admin.members[0], pouet)

        # Try to retrieve a non-existing group
        group = self.manager.get_group("pipo", TEST_CHAN)
        self.assertIsNone(group)

        # Add a second user to the group
        pipo, chan = self.add_known_user(TEST_CHAN, "pipo@domain.tld", "pipo")
        group = self.manager.add_user_to_group("admin", TEST_CHAN, "pipo")
        # The group now contains pipo and pouet
        self.assertEqual(len(group.members), 2)
        self.assertEqual(group.members[0], pouet)
        self.assertEqual(group.members[1], pipo)

        # Remove an user from the group
        user = self.manager.remove_user_from_group("admin", TEST_CHAN, "pipo")
        self.assertEqual(user, pipo)

        # Retrieve the group and check that it contains only pouet
        admin = self.manager.get_group("admin", TEST_CHAN)
        self.assertEqual(len(group.members), 1)
        self.assertEqual(group.members[0], pouet)

        # Remove a group
        group = self.manager.remove_group("admin", TEST_CHAN)
        self.assertEqual(group, admin)

        # Check that the group was removed
        admin = self.manager.get_group("admin", TEST_CHAN)
        self.assertIsNone(admin)
