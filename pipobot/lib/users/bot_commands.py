from pipobot.lib.modules import SyncModule, answercmd, defaultcmd
from pipobot.lib.users.exceptions import NoKnownUser, NicknameConflict


class CmdKnownUser(SyncModule):
    def __init__(self, bot):
        desc = {"": "Known User management",
                "register": "\nuser register <pseudo> [registered_pseudo]: register user <pseudo> from the room to the database",
                "create": "\nuser create <pseudo> <jids>: create a new user with <pseudo> in the database and jids <jids>",
                "show": "user show <who> : show informations about <who> (or show all known users if no parameter)",
                "nick": "user nick <pseudo>: change your pseudo to <pseudo> in this room",
                "list": "list all known users"}

        SyncModule.__init__(self, bot, desc=desc, name="user")

    @defaultcmd
    def rtfm(self, sender):
        return "See !help user for details on available commands : %s" % ",".join(self.desc.iterkeys())

    @answercmd(r'create (?P<pseudo>\S+)(?P<jids>.*)')
    def create(self, sender, pseudo, jids):
        manager = self.bot.KUmanager
        sender = self.bot.users.getuser(sender)
        jids = jids.strip().split()

        if sender.role != "moderator":
            return _("You must be an XMPP moderator of the room to create new users, you are just a %s !" % sender.role)

        try:
            assoc = manager.get_assoc_user(pseudo=pseudo, chan=self.bot.chatname)
            return _("A user is already register with the nickname %s in this room !" % pseudo)
        except NoKnownUser:
            pass

        user = None
        for jid in jids:
            try:
                user = manager.get_known_user(jid=jid)
            except NoKnownUser:
                pass

        if user is None:
            user = manager.create_known_user(jids)

        # All jids are associated to the same person so we can use jids[0]
        assoc = manager.set_nickname(jids[0], self.bot.chatname, pseudo)
        return _("User %s is now one of us !" % pseudo)


    @answercmd(r"register\s+(?P<pseudo>\S+)", r"register(?P<pseudo>)\s+(?P<alias>\S*)")
    def register(self, sender, pseudo="", alias=""):
        if alias == "":
            alias = pseudo
        sender = self.bot.users.getuser(sender)

        if sender.role != "moderator":
            return _("You must be an XMPP moderator of the room to create new users, you are just a %s !" % sender.role)

        target = self.bot.users.getuser(pseudo)
        if target is None:
            return _("%s is not present in the room : you should use ':user create' and provide jids" % pseudo)

        try:
            target.create_known_user(self.bot.KUmanager, alias)
            return _("User %s with jid %s sucessfully created !") % (alias, target.jid)
        except NicknameConflict:
            return _("A user is already registered with the name %s" % alias)

    @answercmd("list")
    def list_users(self, sender):
        msg = ""
        chan = self.bot.chatname
        all_users = self.bot.KUmanager.get_all_users(chan)

        for user in all_users:
            msg += _("%s with jid(s) %s") % (user.nickname, user.user.print_jids())
            if user.live is not None:
                msg += _(", present in this room as %s") % user.live.nickname
            msg += "\n"

        return _("Nobody is registered here !") if msg == "" else msg.strip()

    @answercmd("show", r"show\s+(?P<pseudo>\S+)")
    def show(self, sender, pseudo=""):
        if pseudo == "":
            pseudo = sender

        # Searchs in the KU database someone registered as <pseudo>
        try:
            ku = self.bot.KUmanager.get_assoc_user(pseudo, self.bot.chatname)
            msg = _("User %s is registered as %s in the database with jid(s) %s" % (pseudo, ku.nickname,
                                                                                    ku.print_jids()))
            if ku.live is not None:
                msg += _(" and is here with us with the name %s") % ku.live.nickname
            return msg
        except NoKnownUser:
            pass

        # Checks if the user <pseudo> *in the room* is registered
        target = self.bot.users.getuser(pseudo)

        if target is None:
            return _("There is no user %s in the room, or registered with this nickname" % (pseudo))
        try:
            return _("User %s is registered as %s in the database with jids %s" % (pseudo, target.known.nickname,
                                                                                   target.known.print_jids()))
        except NoKnownUser:
            return _("User %s is in the room but not registered (yet)" % pseudo)

    @answercmd(r"nick (?P<pseudo>\S+)")
    def nick(self, sender, pseudo):
        sender = self.bot.users.getuser(sender)

        try:
            sender.assoc_user_chan()
        except NoKnownUser:
            return _("You must be registered in the room to change your nickname (see :user register)")

        try:
            sender.register_to_room(pseudo)
            return _("Your nickname in this chan is now %s" % pseudo)
        except NicknameConflict:
            return _("User %s already exist in this chan !" % pseudo)
