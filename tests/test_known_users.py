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

    def test_add_knownuser(self):
        # Create a room
        chan = self.manager.create_chan(TEST_CHAN)

        # Add a KnownUser
        pouet = self.manager.create_known_user(["pouet@domain.tld"])
        self.assertNotEqual(pouet, None)

        # Add the user to the room with nickname 'pouet'
        ret = self.manager.set_nickname("pouet@domain.tld", TEST_CHAN, "pouet")
        self.assertEqual(ret.chans[0].nickname, "pouet")
        self.assertEqual(ret, pouet)

        # Get a KnownUser
        assoc = self.manager.get_known_user("pouet", TEST_CHAN)
        self.assertEqual(assoc.nickname, "pouet")

        # Add a KnownUser that already exists : returns None and does nothing
        add = self.manager.create_known_user(["pouet@domain.tld"])
        self.assertEqual(add, None)

    def test_change_nick(self):
        # Create a room
        chan = self.manager.create_chan(TEST_CHAN)

        # Add two KnownUser
        pouet = self.manager.create_known_user(["pouet@domain.tld"])
        self.assertNotEqual(pouet, None)

        pipo = self.manager.create_known_user(["pipo@domain.tld"])
        self.assertNotEqual(pipo, None)

        # Add users to the room with nicknames 'pouet' and 'pipo'
        ret = self.manager.set_nickname("pouet@domain.tld", TEST_CHAN, "pouet")
        self.assertEqual(ret.chans[0].nickname, "pouet")
        self.assertEqual(ret, pouet)
        ret = self.manager.set_nickname("pipo@domain.tld", TEST_CHAN, "pipo")
        self.assertEqual(ret.chans[0].nickname, "pipo")
        self.assertEqual(ret, pipo)

        # Change the nickname of "pouet" to "plop"
        self.manager.change_nickname("pouet", "plop", TEST_CHAN)
        # Check that the user known as "plop" is the same has "pouet" used to be
        plop = self.manager.get_known_user("plop", TEST_CHAN)
        self.assertEqual(plop.user, pouet)

        # Try to change the nickname of a user who does not exist : return None and do nothing
        ret = self.manager.change_nickname("unknown", "pipo", TEST_CHAN)
        self.assertEqual(ret, None)

        # Try to use a new nickname that already exists : nothing happens, "plop" is still "plop"
        ret = self.manager.change_nickname("plop", "pipo", TEST_CHAN)
        self.assertEqual(plop.nickname, "plop")
        self.assertEqual(ret, None)

    def test_group(self):
        # Create a room
        chan = self.manager.create_chan(TEST_CHAN)

        # Create a group
        group = self.manager.create_group("admin", TEST_CHAN)
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)

        # Creates a new user
        pouet = self.manager.create_known_user(["pouet@domain.tld"])
        # Register the user to the chan
        ret = self.manager.set_nickname("pouet@domain.tld", TEST_CHAN, "pouet")

        # Add the user to the group
        group = self.manager.add_user_to_group("admin", TEST_CHAN, "pouet")
        # Check that we modified the appropriate group
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)
        # Check that the user were correctly added to the group
        self.assertEqual(group.members[0], pouet)

        # Try to retrieve a group
        group = self.manager.get_group("admin", TEST_CHAN)
        # Check that we got the appropriate group
        self.assertEqual(group.groupname, "admin")
        self.assertEqual(group.chan, chan)
        # Check that the user is still in the group
        self.assertEqual(group.members[0], pouet)

        # Try to retrieve a non-existing group
        group = self.manager.get_group("pipo", TEST_CHAN)
        self.assertEqual(group, None)
