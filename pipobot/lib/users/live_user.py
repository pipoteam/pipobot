from pipobot.lib.users.exceptions import NoKnownUser


class UserManager(object):
    def __init__(self):
        self.users = {}

    def add_user(self, nickname, jid, role, chan):
        self.users[nickname] = LiveUser(nickname, jid, role, chan)

    def rm_user(self, nickname):
        del self.users[nickname]

    def getuser(self, nickname):
        try:
            return self.users[nickname]
        except KeyError:
            return None

    def known_to_live(self, participant):
        search_chan = participant.chan_id
        search_jid = [jid.jid for jid in participant.user.jids]
        for nick, user in self.users.iteritems():
            if user.chan == search_chan and user.jid in search_jid:
                return user


class LiveUser(object):
    def __init__(self, nickname, jid, role, chan):
        self.nickname = nickname
        self.jid = jid
        self.role = role
        self.chan = chan

    def known_user(self, manager):
        """ :raises: NoKnownUser """
        return manager.get_known_user(chan=self.chan, jid=self.jid)

    def assoc_user_chan(self, manager):
        return manager.get_assoc_user(chan=self.chan, jid=self.jid)

    def create_known_user(self, manager, nickname=None):
        """ :raises: NicknameConflict """
        if nickname is None:
            nickname = self.nickname

        try:
            user = manager.get_known_user(jid=self.jid)
        except NoKnownUser:
            user = manager.create_known_user([self.jid])

        assoc = manager.set_nickname(self.jid, self.chan, nickname)
        return assoc
