class NoGroupFound(Exception):
    def __init__(self, groupname, chan):
        self.groupname = groupname
        self.chan = chan

    def __str__(self):
        return "There is no group %s in the chan %s" % (self.groupname, self.chan)


class NoKnownUser(Exception):
    def __init__(self, pseudo=None, chan=None, jid=None):
        self.pseudo=pseudo
        self.chan = chan
        self.jid = jid

    def __str__(self):
        if self.pseudo is not None and self.chan is not None:
            return "No KnownUser with pseudo %s on chan %s" % (self.pseudo, self.chan)
        elif self.jid is not None:
            return "No KnownUser with jid %s" % self.jid


class RequestError(Exception):
    pass


class JIDConflict(Exception):
    pass


class ChanConflict(Exception):
    pass


class NicknameConflict(Exception):
    def __init__(self, nickname, chan):
        self.nickname = nickname
        self.chan = chan

    def __str__(self):
        return "A user already has the nickname %s in the chan %s" % (self.nickname, self.chan)


class GroupConflict(Exception):
    def __init__(self, groupname, chan):
        self.groupname = groupname
        self.chan = chan

    def __str__(self):
        return "A group named %s already exists in chan %s" % (self.groupname, self.chan)


class GroupMemberConflict(Exception):
    def __init__(self, groupname, chan, nickname):
        self.groupname = groupname
        self.chan = chan
        self.nickname = nickname

    def __str__(self):
        return "%s is already a member of %s in chan %s" % (self.nickname, self.groupname, self.chan)


class GroupMemberError(Exception):
    def __init__(self, groupname, chan, nickname):
        self.groupname = groupname
        self.chan = chan
        self.nickname = nickname

    def __str__(self):
        return "User %s not in group %s for chan %s !" % (self.nickname, self.groupname, self.chan)
