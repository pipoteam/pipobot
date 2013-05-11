from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
from pipobot.bot_test import TestBot
from pipobot.lib.users.known_users import KnownUserManager
from pipobot.lib.bdd import Base
from pipobot.lib.users.exceptions import ChanConflict

DOMAIN = "domain.tld"
CHAN = "test@%s" % DOMAIN


class TestLiveUser(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        self.bot = TestBot("pipotest", "login", CHAN, [], session)
        self.manager = KnownUserManager(self.bot)

    def _create_room(self, chan):
        # Create a room
        try:
            chan = self.manager.create_chan(chan)
        except ChanConflict:
            pass
        return chan


    def add_known_user(self, chan, jid, nickname):
        # Create a room
        chan = self._create_room(chan)

        # Add a KnownUser
        usr = self.manager.create_known_user([jid])
        self.assertIsNotNone(usr)

        # Add the user to the room with nickname 'pouet'
        ret = self.manager.set_nickname(jid, CHAN, nickname)
        self.assertEqual(ret.nickname, nickname)
        self.assertEqual(ret.user, usr)
        return usr, chan

    def test_join_leave(self):
        self.bot.users.add_user("XMPPpouet", "pouet@domain.tld", "moderator", CHAN)
        self.add_known_user(CHAN, "pouet@domain.tld", "pouet")

        # Get a KnownUser
        assoc = self.manager.get_assoc_user(pseudo="pouet", chan=CHAN)
        # Check its registered nickname
        self.assertEqual(assoc.nickname, "pouet")
        # Check its current nickname in the room
        self.assertEqual(assoc.live.nickname, "XMPPpouet")

        self.bot.users.rm_user("XMPPpouet")
        self.assertEqual(assoc.live, None)

    def test_live(self):
        # If pipo is not in the room, we can't find him
        self.assertEqual(self.bot.users.getuser("pipo"), None)

        # pipo, with jid pipo@domain.tld joins the room
        self.bot.users.add_user("pipo", "pipo@%s" % DOMAIN, "administrator", CHAN)

        # We search for the associated KnownUser
        live_pipo = self.bot.users.getuser("pipo")
        # 'pipo' is not registered in the database yet
        self.assertIsNone(live_pipo.known)

        self._create_room(CHAN)

        # We register pipo to the database
        live_pipo.register_to_room()

        registered_pipo = self.bot.users.getuser("pipo").known

        # Verify that the LiveUser.register_to_room works correctly
        self.assertEqual(registered_pipo.nickname, "pipo")
        self.assertEqual(registered_pipo.chan_id, CHAN)
        bdd_pipo = self.manager.get_assoc_user("pipo", CHAN)
        self.assertEqual(bdd_pipo, registered_pipo)

        # From the LiveUser live_pipo, we can retrieve the KnownUser
        self.assertEqual(live_pipo.known, registered_pipo)

        # From a ChanParticipant we can retrieve the LiveUser
        self.assertEqual(bdd_pipo.live, live_pipo)

        # When pipo leaves the room, the ChanParticipant.live becomes None
        self.bot.users.rm_user("pipo")
        self.assertEqual(bdd_pipo.live, None)
