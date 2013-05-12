from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
import pipobot.lib.users.bot_commands
from pipobot.translation import setup_i18n
from pipobot.bot_test import TestBot
from pipobot.lib.users.known_users import KnownUserManager
from pipobot.lib.bdd import Base
from pipobot.lib.users.exceptions import ChanConflict

DOMAIN = "domain.tld"
CHAN = "test@%s" % DOMAIN

class FakeUser:
    def __init__(self, name, bot, jid, role, chan, tester):
        self.name = name
        self.bot = bot
        self.jid = jid
        self.role = role
        self.chan = chan
        self.tester = tester
        self.bot.users.add_user(name, jid, role, chan)

    def ask(self, msg, expected):
        self.tester.assertEqual(self.bot.create_msg(self.name, msg), expected)

    def change_nick(self, new_nick):
        self.bot.users.rm_user(self.name)
        self.name = new_nick
        self.bot.users.add_user(new_nick, self.jid, self.role, self.chan)

    def leave(self):
        self.bot.users.rm_user(self.name)


class TestLiveUser(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        mod = pipobot.lib.users.bot_commands.CmdKnownUser
        setup_i18n("en")
        self.bot = TestBot("pipotest", "login", CHAN, [mod], session)
        self.manager = KnownUserManager(self.bot)

    def _create_room(self, chan):
        # Create a room
        try:
            chan = self.manager.create_chan(chan)
        except ChanConflict:
            pass
        return chan

    def test(self):
        # Some aliasse to make the test more readable
        bob = FakeUser("bob", self.bot, "bob@domain.tld", "participant", CHAN, self)
        admin = FakeUser("admin", self.bot, "admin@domain.tld", "moderator", CHAN, self)

        # Create the room in the database
        self._create_room(CHAN)

        answer = bob.ask(":user list",
                         "Nobody is registered here !")

        # Bob has no 'power' in the room and is not registered : he can't register
        answer = bob.ask(":user register bob",
                         "You must be an XMPP moderator of the room to create new users, you are just a participant !")

        # admin is a moderator : he can register bob
        answer = admin.ask(":user register bob",
                           "User bob with jid bob@domain.tld sucessfully created !")

        # A user uses bob's nickname and we try to register him
        bob.leave()
        bob = FakeUser("bob", self.bot, "wrong@domain.tld", "participant", CHAN, self)

        # Nickname conflict !
        answer = admin.ask(":user register bob",
                           "A user is already registered with the name bob")

        # We can try with an alias : register wrong@domain.tld to 'fakebob'
        answer = admin.ask(":user register bob fakebob",
                           "User fakebob with jid wrong@domain.tld sucessfully created !")

        answer = bob.ask(":user show",
                         "User bob is registered as fakebob in the database with jid(s) wrong@domain.tld")

        # Try to register someone who is not in the room : FAIL
        answer = admin.ask(":user register fail",
                           "fail is not present in the room : you should use ':user create' and provide jids")

        # So we listen to the bot, and user create
        answer = admin.ask(":user create fail fail@domain.tld",
                           "User fail is now one of us !")

        answer = admin.ask(":user show",
                           "User admin is in the room but not registered (yet)")

        # admin is moderator of the room, he can register himself !
        answer = admin.ask(":user register",
                           "User admin with jid admin@domain.tld sucessfully created !")

        # admin can now see its informations
        answer = admin.ask(":user show",
                           "User admin is registered as admin in the database with jid(s) admin@domain.tld")

        # Admin changes its nickname to admin_incognito
        admin.change_nick("admin_incognito")

        # But the bot still knows it's him thanks to its jid
        answer = admin.ask(":user show",
                           "User admin_incognito is registered as admin in the database with jid(s) admin@domain.tld")

        answer = bob.ask(":user show admin",
                         "User admin is registered as admin in the database with jid(s) admin@domain.tld and is here with us with the name admin_incognito")

        answer = admin.ask(":user list",
                           """admin with jid(s) admin@domain.tld, present in this room as admin_incognito
bob with jid(s) bob@domain.tld
fail with jid(s) fail@domain.tld
fakebob with jid(s) wrong@domain.tld, present in this room as bob""")
