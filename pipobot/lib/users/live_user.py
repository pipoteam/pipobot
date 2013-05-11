from pipobot.lib.users.exceptions import NoKnownUser


class UserManager(object):
    def __init__(self, bot):
        self.users = {}
        self.bot = bot

    def add_user(self, nickname, jid, role, chan):
        self.users[nickname] = LiveUser(nickname, jid, role, chan, self.bot)

    def rm_user(self, nickname):
        try:
            self.users[nickname].assoc_user_chan().live = None
            del self.users[nickname]
        except NoKnownUser:
            pass

    def getuser(self, nickname):
        try:
            return self.users[nickname]
        except KeyError:
            return None

    def getuser_byjid(self, jids):
        for user in self.users.itervalues():
            if user.jid in jids:
                return user


class LiveUser(object):
    def __init__(self, nickname, jid, role, chan, bot):
        self.nickname = nickname
        self.jid = jid
        self.role = role
        self.chan = chan
        self.bot = bot

    def get_known(self):
        """ :raises: NoKnownUser """
        try:
            return self.bot.KUmanager.get_known_user(jid=self.jid)
        except NoKnownUser:
            return None

    def assoc_user_chan(self):
        try:
            return self.bot.KUmanager.get_assoc_user(chan=self.chan, jid=self.jid)
        except NoKnownUser:
            return None

    known = property(assoc_user_chan)

    def register_to_room(self, nickname=None):
        """ :raises: NicknameConflict """
        manager = self.bot.KUmanager
        if nickname is None:
            nickname = self.nickname

        try:
            user = manager.get_known_user(jid=self.jid)
        except NoKnownUser:
            user = manager.create_known_user([self.jid])

        manager.set_nickname(self.jid, self.chan, nickname)
