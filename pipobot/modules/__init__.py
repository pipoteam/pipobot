#! /usr/bin/env python2
#-*- coding: utf-8 -*-
""" This module contains all interfaces and general code 
    for modules """

import imp
import inspect
import logging
import re
import sys
import threading
import time
import traceback
logger = logging.getLogger('pipobot.modules') 

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
    """ A general exception that modules will be able to raise """

    def __init__(self, desc) :
        self.desc = desc

    def __unicode__(self) :
        return self.desc

class BotModule(object) :
    """ Defines a basic bot module. Will be subclassed by different types
    of modules than will then by subclassed by actual modules """
    __usable = False
    
    def __init__(self, bot, desc) :
        self.bot = bot
        self.desc = desc
        self.prefixs = ['!', ':', self.bot.name+':', self.bot.name+',']

    def do_answer(self, mess) :
        """ With an xmpp message `mess`, checking if this module is concerned
            by it, and if so get the result of the module and make the bot
            say it """

        msg_body = mess.getBody().lstrip()
        sender = mess.getFrom().getResource()
        
        #The bot does not answer to itself (important to avoid some loops !)
        if sender == self.bot.name:
            return
       
        #Check if the message is related to this module
        if not self.is_concerned(msg_body) :
            return
        
        #If `mess` is a private message but privmsg are not allowed for the module
        if mess.getType() == "chat" and not self.pm_allowed :
            return

        try :
            #Calling the answer method of the module
            if isinstance(self, SyncModule)  :
                # Separates command/args and get answer from module
                command, args =  self.parse(msg_body, self.prefixs)
                send = self._answer(sender, args)
            elif isinstance(self, ListenModule) :
                # In a Listen module the name of the command is not specified 
                # so nothing to parse
                send = self.answer(sender, msg_body)
            elif isinstance(self, MultiSyncModule) :
                # Separates command/args and get answer from module
                command, args =  SyncModule.parse(msg_body, self.prefixs)
                send = self._answer(sender, command, args)
            else :
                # A not specified module type !
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
                    self.bot.say("Error from module %s: %s" % (command, send))
        except:
            self.bot.say(_("Error !"))
            logger.error("Error from module %s: %s" % (self.__class__, traceback.format_exc()))

    def _dict_messages(self, send, mess, priv=None) :
        """ Creates messages with a dictionnary described as :
               {"text": raw_message,    # Text message, transform XHTML if empty
                "xhtml" : xhtml_message # XHTML message
                "monospace" : True      # XHTML message is the text with monospace
                "users" : { "pseudo1" : {...} } # Send the same type of dictionnary
                                                  in private to the users
               }"""
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
    __usable = False

    def __init__(self, bot, desc, command, pm_allowed=True, lock_time = -1) :
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
        if lock_time > 0:
            self.lock_time = lock_time
            self.lock_name = "%s_lock" % self.__class__.__name__
            self.enable()

    @staticmethod
    def parse(body, prefixs) :
        command = None
        for prefix in prefixs :
            if body.startswith(prefix) :
                command = body[len(prefix):].strip()
                break
        return command.partition(' ')[::2] if command is not None else (None, None)
    
    def is_concerned(self, body) :
        return SyncModule.parse(body, self.prefixs)[0] == self.command

    def enable(self):
        setattr(self.bot, self.lock_name, False)

    def disable(self):
        setattr(self.bot, self.lock_name, True)
        t = threading.Timer(self.lock_time, self.enable)
        t.start()

    def _answer(self, sender, args) :
        # if this command is called by !cmd arg1 arg2 arg3 then args = 'arg1 arg2 arg3'
        #if self.bot
        if hasattr(self, "lock_name"):
            if getattr(self.bot, self.lock_name):
                return _("Please do not flood !")
            else:
                self.disable()
        args = args.strip()
        splitted_args = args.split(" ", 1)
        cmd_name = splitted_args[0].strip()
        cmd_args = splitted_args[1].strip() if len(splitted_args) > 1 else ""

        for key in self.fcts.keys():
            # if in the module there is a method with @answercmd(cmd_name)
            if key == cmd_name:
                try:
                    return self.fcts[cmd_name](sender, cmd_args)
                except KeyError:
                    return _("The %s command requires args") % self.command
            else:
                # We check if the method is not defined by a regexp matching cmd_name
                s = re.match(key, args)
                if s != None:
                    return self.fcts[key](sender, s)
        try:
            return self.fcts["default"](sender, args)
        except KeyError:
            return "La commande %s n'existe pas pour %s ou la syntaxe de !%s %s est incorrecte → !help %s pour plus d'information" %  \
                        (cmd_name, self.command, self.command, cmd_name, self.command)

    def help(self, body):
        if body == self.command:
            return self.desc
        
class MultiSyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command defined in a list. """
    __usable = False

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
            raise ModuleException(_("Command %s not handled by this module") % command)

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
    __usable = False
    
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
    __usable = False

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
        desc = {"" : _("Display help for modules"), 
                "module" : _("help [module] : show the full help for a module"),
                "subcom" : _("help module [subcom] : show the help for a sub-command of a module")}
        SyncModule.__init__(self, bot, desc, "help")
        self.compact_help_content = ""
        self.genHelp()

    @defaultcmd
    def answer(self, sender, args) :
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
        return {"text" : res, "monospace" : True}

    def genHelp(self):
        sync_lst = []
        listen_lst = []
        multi_lst = []
        pres_lst = []
        for cmd in self.bot.modules:
            if isinstance(cmd, SyncModule):
                sync_lst.append(cmd.command)
            elif isinstance(cmd, ListenModule):
                listen_lst.append(cmd.name)
            elif isinstance(cmd, MultiSyncModule):
                multi_lst.extend(cmd.commands.keys())
            elif isinstance(cmd, PresenceModule):
                pres_lst.append(cmd.name)
        delim = "*"*10
        sync = _("%s[Sync commands]%s\n%s") % (delim, delim, Help.genString(sorted(sync_lst)))
        listen = _("%s[Listen commands]%s\n%s") % (delim, delim, Help.genString(sorted(listen_lst)))
        multi = _("%s[Multi commands]%s\n%s") % (delim, delim, Help.genString(sorted(multi_lst)))
        pres = _("%s[Presence commands]%s\n%s") % (delim, delim, Help.genString(sorted(pres_lst)))
        self.all_help_content = "\n%s\n%s\n%s\n%s" % (sync, listen, multi, pres)
        allcmds = sync_lst + multi_lst
        self.compact_help_content = _("I can execute: \n%s") % Help.genString(sorted(allcmds))

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


###############################################################################################
##################################  PRESENCE MODULES  #########################################
###############################################################################################

class PresenceModule(BotModule):
    """ Defines a bot module that will receive all
    the presence sent on the chatroom and call answer
    on it. Be careful with those modules"""
    __usable = False

    def __init__(self, bot, name, desc, pm_allowed=True):
        BotModule.__init__(self, bot, desc)
        self.name = name
        self.pm_allowed = pm_allowed

    def help(self, body):
        if body == self.name:
            return self.desc


class RecordUsers(PresenceModule):
    def __init__(self, bot):
        desc = _("Recording users logins/logout")
        PresenceModule.__init__(self,
                                bot,
                                name = "recordusers",
                                desc = desc)

    def do_answer(self, message):
        role = ""
        jid = ""

        #Get the role of the participant
        for xtag in message.getTags("x"):
            if xtag.getTag("item"):
                role = xtag.getTag("item").getAttr("role")

        pseudo = message.getFrom().getResource()

        #The user [pseudo] leaves the room
        if message.getType() == 'unavailable':
            self.bot.occupants.rm_user(pseudo)
        else:
            if message.getJid() is not None:
                jid = message.getJid().split("/")[0]
            self.bot.occupants.add_user(pseudo, jid, role)


###############################################################################################
########################################  IQ MODULES  #########################################
###############################################################################################

class IQModule(BotModule):
    __usable = False

    def __init__(self, bot, name, desc, pm_allowed=True):
        BotModule.__init__(self, bot, desc)
        self.name = name
        self.pm_allowed = pm_allowed

    def help(self, body):
        if body == self.name:
            return self.desc


class BotModuleLoader(object):
    def __init__(self, extra_modules_paths=None, module_settings=None):
        self._orig_path = sys.path
        additional_paths = list(__path__)
        if extra_modules_paths:
            additional_paths.extend(extra_modules_paths)
        
        sys.path = list(self._orig_path)
        for module_path in additional_paths:
            if module_path not in sys.path:
                sys.path.insert(0, module_path)
        
        self._module_settings = module_settings or {}
        self._module_cache = {}
    
    @staticmethod
    def is_bot_module(obj):
        """
        Returns True if an object found in a Python module is a bot module
        class.
        """
    
        return (inspect.isclass(obj) and issubclass(obj, BotModule)
            and not hasattr(obj, '_%s__usable' % obj.__name__))
    
    def get_modules(self, module_names):
        """
        Returns a list of bot commands from the passed module names.
        """
    
        modules = []
        
        for name in module_names:
            if name in self._module_cache:
                modules.extend(self._module_cache[name])
                continue
            
            try:
                module_info = imp.find_module(name)
            except ImportError:
                sys.stderr.write("Module ‘%s’ was not found.\n" % name)
                sys.exit(1)
            
            try:
                module_data = imp.load_module(name, *module_info)
            except Exception as exc:
                sys.stderr.write("Module ‘%s’ failed to load.\n" % name)
                traceback.print_exc()
                sys.exit(1)
            
            bot_modules = inspect.getmembers(module_data, self.is_bot_module)
            bot_modules = [item[1] for item in bot_modules]
            
            if name in self._module_settings:
                logger.debug("Configuration for ‘%s’: %s", name,
                    self._module_settings[name])
                for module in bot_modules:
                    module._settings = self._module_settings[name]
            
            logger.debug("Bot modules for ‘%s’ : %s", name, bot_modules)
            
            modules.extend(bot_modules)
            self._module_cache[name] = bot_modules
        
        
        modules.append(RecordUsers)
        modules.append(Help)
        return modules
        
    def cleanup(self):
        """
        Should be called after the calls to get_modules. Restores the
        original system path.
        """
    
        sys.path = self._orig_path
