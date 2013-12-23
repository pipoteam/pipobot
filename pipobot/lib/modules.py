#! /usr/bin/env python2
#-*- coding: utf-8 -*-
""" This module contains all interfaces and general code
    for modules """

import inspect
import logging
import re
import threading
import time
import traceback
logger = logging.getLogger('pipobot.lib.modules')


def defaultcmd(funct):
    """This defines a decorator to indicate the default answer method
        for a module"""
    setattr(funct, "dflcommand", True)
    return funct


def answercmd(*args):
    """This defines a decorator to indicate a valid command for a module"""
    def wrapper(fct):
        setattr(fct, "subcommand", args)
        return fct
    return wrapper


class ModuleException(Exception):
    """ A general exception that modules will be able to raise """
    pass


class BotModule(object):
    """ Defines a basic bot module. Will be subclassed by different types
    of modules than will then by subclassed by actual modules """
    __usable = False

    def __init__(self, bot, desc):
        self.bot = bot
        self.desc = desc
        #Valid prefixes are : "!", ":" or "bot_name[:|,] [!|:]"
        self.prefixs = []
        base_prefixs = ["!", ":"]

        for prefix in base_prefixs:
            self.prefixs.append("%s, %s" % (self.bot.name, prefix))
            self.prefixs.append("%s: %s" % (self.bot.name, prefix))

        self.prefixs.extend(base_prefixs)

    def do_answer(self, mess):
        """ With an xmpp message `mess`, checking if this module is concerned
            by it, and if so get the result of the module and make the bot
            say it """

        msg_body = mess["body"].lstrip()
        sender = mess["from"].resource

        #The bot does not answer to itself (important to avoid some loops !)
        if sender == self.bot.name:
            return

        #Check if the message is related to this module
        if not self.is_concerned(msg_body):
            return

        try:
            #Calling the answer method of the module
            if isinstance(self, SyncModule):
                # Separates command/args and get answer from module
                command, args = SyncModule.parse(msg_body, self.prefixs)
                send = self._answer(sender, args, pm=(mess["type"] == "chat"))
            elif isinstance(self, ListenModule):
                # In a Listen module the name of the command is not specified
                # so nothing to parse
                send = self.answer(sender, msg_body)
            elif isinstance(self, MultiSyncModule):
                # Separates command/args and get answer from module
                command, args = SyncModule.parse(msg_body, self.prefixs)
                send = self._answer(sender, command, args, pm=(mess["type"] == "chat"))
            else:
                # A not specified module type !
                return

            return send
        except:
            self.bot.say(_("Error !"))
            logger.error(_("Error from module %s : %s") % (self.__class__,
                                                           traceback.format_exc().decode("utf-8")))

    def is_concerned(self, msg) :
        raise NotImplementedError("Must be subclassed")

    def answer(self, *args, **kwargs) :
        raise NotImplementedError("Must be subclassed")

    def _answer(self, *args, **kwargs) :
        raise NotImplementedError("Must be subclassed")

class SyncModule(BotModule):
    """ Defines a bot module that will answer/execute an action
    after a command. This is the most common case """
    __usable = False
    shortname = "sync"

    def __init__(self, bot, desc, name, pm_allowed=True, lock_time=1):
        BotModule.__init__(self, bot, desc)
        self.name = name
        self.fcts = []
        self.default_cmd = None
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                if method.dflcommand:
                    if self.default_cmd is not None :
                        logger.warn("Another default command defined for this module, the other will be ignored")
                    else :
                        self.default_cmd = method
            except AttributeError :
                pass
            try:
                regexp = getattr(method, "subcommand")
                if type(regexp) == tuple:
                    for sub_re in regexp:
                        self.fcts.append((sub_re, method))
                else:
                    self.fcts.append((regexp, method))
            except AttributeError:
                pass
        if lock_time > 0:
            self.lock_time = lock_time
            self.lock_name = "%s_lock" % self.__class__.__name__
            self.enable()
        self.pm_allowed = pm_allowed

    @staticmethod
    def parse(body, prefixs):
        """Parses a command to extract command_name and args"""
        command = None
        for prefix in prefixs:
            if body.startswith(prefix):
                command = body[len(prefix):].strip()
                break
        return command.partition(' ')[::2] if command is not None else (None, None)

    def is_concerned(self, body):
        """Checks if a message [body] is in fact a call to this module"""
        return SyncModule.parse(body, self.prefixs)[0] == self.name

    def enable(self):
        """Unsets the lock attribute which prevent a user from flooding
            using this command"""
        setattr(self.bot, self.lock_name, False)

    def disable(self):
        """Sets the lock attribute which prevent a user from flooding
            using this command"""
        setattr(self.bot, self.lock_name, True)
        t = threading.Timer(self.lock_time, self.enable)
        t.start()

    def _answer(self, sender, args, pm=False):
        # If `mess` is a private message but privmsg are not allowed for the module
        if pm and not self.pm_allowed:
            return

        if hasattr(self, "lock_name"):
            if getattr(self.bot, self.lock_name):
                return _("Please do not flood !")
            else:
                self.disable()
        args = args.strip()
        cmd_name = args.split(" ", 1)[0].strip()

        for regexp, fct in self.fcts:
            # We check if the method is not defined by a regexp matching cmd_name
            m = re.match("^"+regexp+"$", args)
            if m is not None:
                return fct(sender, **m.groupdict())

        # No function were found
        if self.default_cmd is not None:
            return self.default_cmd(sender, args)
        else:
            return "La commande %s n'existe pas pour %s ou la syntaxe de !%s %s est incorrecte → !help %s pour plus d'information" %  \
                        (cmd_name, self.name, self.name, cmd_name, self.name)

    def help(self, body):
        if body == self.name:
            return self.desc


class MultiSyncModule(BotModule):
    """ Defines a bot module that will answer/execute an action
    after a command defined in a list. """
    __usable = False
    shortname = "multisync"

    def __init__(self, bot, names, pm_allowed=True):
        BotModule.__init__(self, bot, '')

        self.names = names
        self.pm_allowed = pm_allowed
        self.fcts = []
        self.default_cmd = None
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                if method.dflcommand:
                    if self.default_cmd is not None :
                        logger.warn("Another default command defined for this module, the other will be ignored")
                    else :
                        self.default_cmd = method
            except AttributeError :
                pass
            try:
                regexp = getattr(method, "subcommand")
                if type(regexp) == tuple:
                    for sub_re in regexp:
                        self.fcts.append((sub_re, method))
                else:
                    self.fcts.append((regexp, method))
            except AttributeError:
                pass

    def is_concerned(self, body):
        return SyncModule.parse(body, self.prefixs)[0] in self.names

    def _answer(self, sender, name, args, pm=False):
        # If `mess` is a private message but privmsg are not allowed for the module
        if pm and not self.pm_allowed:
            return

        if name not in self.names:
            raise ModuleException(_("Command %s not handled by this module") % name)

        if self.default_cmd is not None:
            module_answer = self.default_cmd(name, sender, args)
        else:
            logger.error(_("MultiSyncModule must define a “@defaultcmd” method"))
            module_answer = None
        return module_answer

    def help(self, body):
        for name, desc in self.names.iteritems():
            if body == name:
                return desc

    @property
    def name(self):
        return "_".join(self.names)

class AsyncModule(BotModule, threading.Thread):
    """ Defines a bot module that will be executed as a
    daemon thread. Typically for waiting for asynchronous event
    such as mail, etc... """
    __usable = False
    shortname = "async"

    def __init__(self, bot, name, desc, delay=0):
        threading.Thread.__init__(self)
        BotModule.__init__(self, bot, desc)

        # Thead parameters
        self.alive = True
        self.daemon = True

        # How many seconds between two calls to module's 'action' method
        self.delay = delay
        self.name = name

    def is_concerned(self, command):
        return False

    def run(self):
        while self.alive:
            time.sleep(self.delay)
            try:
                self.action()
            except:
               logger.error(_("Error from module %s : %s") % (self.__class__,
                                                               traceback.format_exc().decode("utf-8")))

    def action(self) :
        raise NotImplementedError("Must be subclassed")

    def stop(self):
        self.alive = False

    def help(self, body):
        if body == self.name:
            return self.desc


class ListenModule(BotModule):
    """ Defines a bot module that will receive all
    the message sent on the chatroom and call answer
    on it. Be careful with those modules"""
    __usable = False
    shortname = "listen"

    def __init__(self, bot, name, desc):
        BotModule.__init__(self, bot, desc)
        self.name = name

    def is_concerned(self, command):
        return True

    def help(self, body):
        if body == self.name:
            return self.desc


class Help(SyncModule):
    """ Defines the help module : when we use the command
        !help _modulename_ it will display the corresponding
        description of the module"""

    def __init__(self, bot):
        desc = "!help name : display the help for the module `name`"
        desc = {"": _("Display help for modules"),
                "module": _("help [module] : show the full help for a module"),
                "subcom": _("help module [subcom] : show the help for a sub-command of a module")}
        SyncModule.__init__(self, bot, desc, "help")
        self.compact_help_content = ""
        self.genHelp()

    @defaultcmd
    def answer(self, sender, args):
        res = _("The command %s does not exist") % args
        if args == "":
            res = self.compact_help_content
        elif args == "all":
            res = self.all_help_content
        else:
            try:
                cmd_name, subcoms = args.split(" ", 1)
            except ValueError:
                cmd_name = args
                subcoms = ""
            for cmd in self.bot.modules:
                hlp = cmd.help(cmd_name)
                if hlp is not None:
                    #res = hlp
                    res = ""
                    if type(hlp) == dict:
                        if subcoms == "subcom":
                            available_subcoms = ", ".join(sorted([key for key in hlp.keys() if key != ""]))
                            desc = " : %s" % hlp[""] if "" in hlp else ""
                            res = _("%s%s\nSub-commands : %s") % (cmd_name, desc, available_subcoms)
                        elif subcoms == "":
                            res = '\n'.join(["%s : %s" % (key, val) for key, val in hlp.iteritems() if key != ""])
                        else:
                            res = []
                            for subcom in subcoms.split(","):
                                subcom = subcom.strip()
                                try:
                                    res.append(hlp[subcom])
                                except KeyError:
                                    pass
                            res = "\n".join(res)
                    else:
                        res = hlp
                    break
        return {"text": res, "monospace": True}

    def genHelp(self):
        multi_lst = []
        modules = self.bot._modules
        for cmd in modules.multisync.values():
            multi_lst.extend(cmd.names.keys())
        sync_lst = sorted(modules.sync.keys())
        listen_lst = sorted(modules.listen.keys())
        pres_lst = sorted(modules.presence.keys())

        delim = "*" * 10
        sync = _(u"%s[Sync commands]%s\n%s") % (delim, delim, Help.genString(sync_lst))
        listen = _(u"%s[Listen commands]%s\n%s") % (delim, delim, Help.genString(listen_lst))
        multi = _(u"%s[Multi commands]%s\n%s") % (delim, delim, Help.genString(multi_lst))
        pres = _(u"%s[Presence commands]%s\n%s") % (delim, delim, Help.genString(pres_lst))
        self.all_help_content = u"\n%s\n%s\n%s\n%s" % (sync, listen, multi, pres)
        allcmds = sync_lst + multi_lst
        self.compact_help_content = _(u"I can execute: \n%s") % Help.genString(sorted(allcmds))

    @staticmethod
    def genString(l):
        send = ""
        i = 0
        while i + 2 < len(l):
            cmd1 = l[i]
            cmd2 = l[i + 1]
            cmd3 = l[i + 2]
            espaces1 = " " * (25 - len(cmd1) - 1)
            espaces2 = " " * (25 - len(cmd2) - 1)
            line = u"-%s%s-%s%s-%s\n" % (cmd1, espaces1, cmd2, espaces2, cmd3)
            send += line
            i += 3
        if i < len(l):
            espaces = " " * (25 - len(l[i]) - 1)
            send += u"-%s%s" % (l[i], espaces)
        if i + 1 < len(l):
            send += u"-%s" % (l[i + 1])
        if i == len(l):
            send = send.rstrip()
        return send


###############################################################################################
##################################  PRESENCE MODULES  #########################################
###############################################################################################


class PresenceModule(BotModule):
    """ Defines a bot module that will receive all
    the presence sent on the chatroom and call answer
    on it. Be careful with those modules"""
    __usable = False
    shortname = "presence"

    def __init__(self, bot, name, desc):
        BotModule.__init__(self, bot, desc)
        self.name = name

    def help(self, body):
        if body == self.name:
            return self.desc


class RecordUsers(PresenceModule):
    def __init__(self, bot):
        desc = _("Recording users logins/logout")
        PresenceModule.__init__(self,
                                bot,
                                name="recordusers",
                                desc=desc)

    def do_answer(self, message):
        pseudo = message["muc"]["nick"]

        #The user [pseudo] leaves the room
        if message["type"] == 'unavailable':
            self.bot.occupants.rm_user(pseudo)
        else :
            role = message["muc"]['role']
            try:
                jid = message["muc"]["jid"].bare
            except AttributeError:
                jid = ""
            self.bot.occupants.add_user(pseudo, jid, role)


###############################################################################################
########################################  IQ MODULES  #########################################
###############################################################################################


class IQModule(BotModule):
    __usable = False
    shortname = "iq"

    def __init__(self, bot, name, desc):
        BotModule.__init__(self, bot, desc)
        self.name = name

    def help(self, body):
        if body == self.name:
            return self.desc

base_class = [AsyncModule, SyncModule, ListenModule, MultiSyncModule, PresenceModule, IQModule]
