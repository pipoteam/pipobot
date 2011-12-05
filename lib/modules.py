#! /usr/bin/env python2
#-*- coding: utf-8 -*-

import threading
import logging
import traceback
import time
import inspect
logger = logging.getLogger('pipobot.lib.modules') 

def defaultcmd(f) :
    #We set a marker to indicate that this method is a valid command
    setattr(f, "subcommand", "default")
    return f

def answercmd(*args):
    def wrapper(fct):
        setattr(fct, "subcommand", args)
        return fct
    return wrapper

class ModuleException(Exception) :

    def __init__(self, desc) :
        self.desc = desc

    def __unicode__(self) :
        return self.desc

class BotModule(object) :
    """ Defines a basic bot module. Will be subclassed by different types
    of modules than will then by subclassed by actual modules """
    

    def __init__(self, bot, desc) :
        self.bot = bot
        self.desc = desc
        self.prefixs = ['!', ':', self.bot.name+':', self.bot.name+',']

    def do_answer(self, mess) :
        msg_body = mess.getBody().lstrip()
        sender = mess.getFrom().getResource()

        if sender == self.bot.name:
            return
        
        if not self.is_concerned(msg_body) :
            return

        if mess.getType() == "chat" and not self.pm_allowed :
            return

        try :
            #Calling the answer method of the module
            if isinstance(self, SyncModule)  :
                command, args =  self.parse(msg_body, self.prefixs)
                send = self._answer(sender, args)
            elif isinstance(self, ListenModule) :
                send = self.answer(sender, msg_body)
            elif isinstance(self, MultiSyncModule)  :
                command, args =  SyncModule.parse(msg_body, self.prefixs)
                send = self._answer(sender, command, args)
            else :
                # ???
                return

            #If the method is just a string, it will be the bot's answer
            if type(send) == str or type(send) == unicode:
                self.bot.say(send, in_reply_to=mess)

            #If it's a list we display each message with a time delay
            elif type(send) == list:
                for line in send:
                    time.sleep(0.3)
                    self.bot.say(line, in_reply_to=mess)
                    
            #If it's a dictionary, it is {"text": raw_message,    # Text message, transform XHTML if empty
            #                             "xhtml" : xhtml_message # XHTML message
            #                             "monospace" : True      # XHTML message is the text with monospace
            #                             "users" : { "pseudo1" : {...} } # Send the same type of dictionnary
            #                                                               in private to the users
            #                            }
            elif type(send) == dict:
               self._dict_messages(send, mess)

            else:
                #In any other case, an error has occured in the module
                if send is not None:
                    self.bot.say(_("Error from module %s : %s") % (command, send))
        except:
            self.bot.say(_("Error !"))
            logger.error(_("Error from module %s : %s") % (self.__class__, traceback.format_exc()))

    def _dict_messages(self, send, mess, priv=None) :
        if "xhtml" in send and "text" in send:
            self.bot.say_xhtml(send["text"], send["xhtml"], priv=priv, in_reply_to=mess)
        elif "text" in send and "monospace" in send and send["monospace"]:
            html_msg = send["text"]
            html_msg = html_msg.replace("&", "&amp;")
            html_msg = html_msg.replace("<", "&lt;")
            html_msg = html_msg.replace(">", "&gt;")
            html_msg = '<p><span style="font-family: monospace">%s</span></p>' % html_msg.replace("\n", "<br/>\n") 
            #TODO others characters to convert ?
            self.bot.say_xhtml(send["text"], html_msg, priv=priv, in_reply_to=mess)
        else:
            self.bot.say(send["text"], priv=priv, in_reply_to = mess)

        if "users" in send :
            for user, send_user in send["users"] :
                self._dict_messages(send_user, mess, priv=user)


class SyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command. This is the most common case """
    def __init__(self, bot, desc, command, pm_allowed=True) :
        BotModule.__init__(self, bot, desc)
        self.command = command
        self.pm_allowed = pm_allowed
        self.fcts = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                handlerarg = getattr(method, "subcommand")
                if type(handlerarg) == tuple:
                    for sub_fct in handlerarg:
                        self.fcts[sub_fct] = method
                else:
                    self.fcts[handlerarg] = method
            except AttributeError:
                pass

    @staticmethod
    def parse(body, prefixs) :
        command = None
        spl = body.split(" ")
        for prefix in prefixs :
            if body.startswith(prefix) :
                command = spl[0][len(prefix):].strip()
                break
        return command, " ".join(spl[1:])
    
    def is_concerned(self, body) :
        return SyncModule.parse(body, self.prefixs)[0] == self.command

    def _answer(self, sender, args) :
        module_answer = "To be implemented"
        splitted_args = args.split(" ", 1)
        if splitted_args == []:
            key = "default"
            error_msg = "La commande %s nécessite des arguments !" % self.command
        else:
            key = splitted_args[0]
            error_msg = "La commande %s n'existe pas pour %s" % (key, self.command)
        cmd_args = splitted_args[1] if len(splitted_args) > 1 else ""
        try:
            module_answer = self.fcts[key](sender, cmd_args)
        except KeyError:
            try:
                module_answer = self.fcts["default"](sender, args)
            except KeyError:
                return error_msg
        return module_answer

    def help(self, body):
        if body == self.command:
            return self.desc
        
class MultiSyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command defined in a list. """

    def __init__(self, bot, commands, pm_allowed=True) :
        BotModule.__init__(self, bot, '')

        self.commands = commands
        self.pm_allowed = pm_allowed
        self.fcts = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                handlerarg = getattr(method, "subcommand")
                if type(handlerarg) == tuple:
                    for sub_fct in handlerarg:
                        self.fcts[sub_fct] = method
                else:
                    self.fcts[handlerarg] = method
            except AttributeError:
                pass

    def is_concerned(self, body) :
        return SyncModule.parse(body, self.prefixs)[0] in self.commands

    def _answer(self, sender, command, args) :
        if command not in self.commands :
            raise ModuleException("Command %s not handled by this module" % command)

        module_answer = self.fcts["default"](command, sender, args)
        return module_answer

    def help(self, body):
        for command, desc in self.commands.iteritems():
            if body == command:
                return desc


class AsyncModule(BotModule, threading.Thread) :
    """ Defines a bot module that will be executed as a
    daemon thread. Typically for waiting for asynchronous event
    such as mail, etc... """
    
    def __init__(self, bot, name, desc, delay = 0, pm_allowed=True) :
        threading.Thread.__init__(self)
        BotModule.__init__(self, bot, desc)

        # Thead parameters
        self.alive = True
        self.daemon = True

        # How many seconds between two calls to module's 'action' method
        self.delay = delay
        self.name = name

        self.pm_allowed = pm_allowed

    def is_concerned(self, command) :
        return False

    def run(self) :
        while self.alive :
            time.sleep(self.delay)
            self.action()

    def stop(self) :
        self.alive = False

    def help(self, body):
        if body == self.name:
            return self.desc

         
class ListenModule(BotModule) :
    """ Defines a bot module that will receive all
    the message sent on the chatroom and call answer
    on it. Be careful with those modules"""

    def __init__(self, bot, name, desc, pm_allowed=True) :
        BotModule.__init__(self, bot, desc)
        self.name = name
        self.pm_allowed = pm_allowed

    def is_concerned(self, command) :
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
        SyncModule.__init__(self, bot, desc, "help")
        self.compact_help_content = ""
        self.genHelp()

    @defaultcmd
    def answer(self, sender, args) :
        if args == "":
            return self.compact_help_content
        elif args == "all":
            return self.all_help_content
        for cmd in self.bot.modules:
            hlp = cmd.help(args)
            if hlp is not None:
                return hlp
        return "La commande %s n'existe pas" % args

    def genHelp(self):
        sync_lst = []
        listen_lst = []
        multi_lst = []
        for cmd in self.bot.modules:
            if isinstance(cmd, SyncModule):
                sync_lst.append(cmd.command)
            elif isinstance(cmd, ListenModule):
                listen_lst.append(cmd.name)
            elif isinstance(cmd, MultiSyncModule):
                multi_lst.extend(cmd.commands.keys())
        delim = "*"*10
        sync = "%s[Sync commands]%s\n%s" % (delim, delim, Help.genString(sorted(sync_lst)))
        listen = "%s[Listen commands]%s\n%s" % (delim, delim, Help.genString(sorted(listen_lst)))
        multi = "%s[Multi commands]%s\n%s" % (delim, delim, Help.genString(sorted(multi_lst)))
        self.all_help_content = "\n%s\n%s\n %s" % (sync, listen, multi)
        allcmds = sync_lst + multi_lst
        self.compact_help_content = "Votre serviteur peut exécuter : \n%s" % Help.genString(sorted(allcmds))

    @staticmethod
    def genString(l):
        send = ""
        i = 0
        while i+2 < len(l):
            cmd1 = l[i]
            cmd2 = l[i+1]
            cmd3 = l[i+2]
            espaces1 = " "*(25 - len(cmd1) - 1)
            espaces2 = " "*(25 - len(cmd2) - 1)
            line = "-%s%s-%s%s-%s\n"%(cmd1, espaces1, cmd2, espaces2, cmd3)
            send += line
            i += 3
        if i < len(l):
            espaces = " "*(25 - len(l[i]) - 1)
            send += "-%s%s"%(l[i], espaces)
        if i +1 < len(l):
            send += "-%s"%(l[i+1])
        if i == len(l):
            send = send[0:-1]
        return send
