from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
from pipobot.lib.users.live_user import LiveUser
from pipobot.lib.users.known_users import KnownUserManager
from pipobot.lib.bdd import Base
from pipobot.lib.users.exceptions import *

DOMAIN = "domain.tld"
CHAN = "test@%s" % DOMAIN


class TestLiveUser(unittest.TestCase):
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
        ret = self.manager.set_nickname(jid, CHAN, nickname)
        self.assertEqual(ret.chans[0].nickname, nickname)
        self.assertEqual(ret, usr)
        return usr, chan

    def test_access(self):
        live_pipo = LiveUser("pipo", "pipo@%s" % DOMAIN, "administrator", CHAN)
        self.assertRaises(NoKnownUser, callable=live_pipo.known_user, args=(self.manager))

        pipo, chan = self.add_known_user(CHAN, "pipo@%s" % DOMAIN, "pipo")
        pouet, chan = self.add_known_user(CHAN, "pouet@%s" % DOMAIN, "pouet")

        self.assertEqual(live_pipo.known_user(self.manager), pipo)
        live_pouet = LiveUser("pouet", "pouet@%s" % DOMAIN, "administrator", CHAN)

        self.assertEqual(live_pipo.known_user(self.manager), pipo)
        self.assertEqual(live_pouet.known_user(self.manager), pouet)

        bdd_pipo = self.manager.get_known_user("pipo", CHAN)

        # Verify that the LiveUser.create_known_user works correctly
        self.assertEqual(bdd_pipo, live_pipo.create_known_user(self.manager))

        # Verify that the getter LiveUser.known_user works correctly
        self.assertEqual(bdd_pipo, live_pipo.known_user(self.manager))

        pipo_chan = self.manager.get_assoc_user(pseudo="pipo", chan=CHAN)
        self.assertEqual(live_pipo.assoc_user_chan(self.manager), pipo_chan)

