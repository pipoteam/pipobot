#! /usr/bin/env python2
#-*- coding: utf-8 -*-

import threading
import logging
import traceback
import time
logger = logging.getLogger('pipobot.lib.modules') 

def answercmd(f) :
    return f

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

        if not self.is_concerned(msg_body) :
            return

        if mess.getType() == "chat" and not self.pm_allowed :
            return

        try :
            #Calling the answer method of the module
            if isinstance(self, SyncModule)  :
                command, args =  self.parse(msg_body, self.prefixs)
                send = self.answer(sender, args)
            elif isinstance(self, ListenModule) :
                send = self.answer(sender, msg_body)
            elif isinstance(self, MultiSyncModule)  :
                command, args =  self.parse(msg_body, self.prefixs)
                send = self.answer(sender, command, args)
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

    @staticmethod
    def parse(body, prefixs) :
        command = None
        spl = body.split(" ")
        for prefix in prefixs :
            if body.startswith(prefix) :
                command = spl[0][len(prefix):]
                break
        return command, " ".join(spl[1:])
    
    def __init__(self, bot, desc, command, pm_allowed=True) :
        BotModule.__init__(self, bot, desc)
        self.command = command
        self.pm_allowed = pm_allowed

    def is_concerned(self, body) :
        return SyncModule.parse(body, self.prefixs)[0] == self.command

    def answer(self, sender, args) :
        return "To be implemented"

        
class MultiSyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command defined in a list. """

    def __init__(self, bot, commands, pm_allowed=True) :
        BotModule.__init__(self, bot, '')

        self.commands = commands
        self.pm_allowed = pm_allowed

    def is_concerned(self, body) :
        return SyncModule.parse(body, self.prefixs)[0] in self.commands

    def answer(self, command, sender, args) :
        if command not in self.commands :
            raise ModuleException("Command %s not handled by this module" % command)

        return "To be implemented"


class AsyncModule(BotModule, threading.Thread) :
    """ Defines a bot module that will be executed as a
    daemon thread. Typically for waiting for asynchronous event
    such as mail, etc... """
    
    def __init__(self, bot, name, desc) :
        threading.Thread.__init__(self)
        BotModule.__init__(self, bot, desc)

        # Thead parameters
        self.alive = True
        self.daemon = True

        self.name = name

    def is_concerned(self, command) :
        return False

    def run(self) :
        while self.alive :
            self.action()

    def stop(self) :
        self.alive = False

         
class ListenModule(BotModule) :
    """ Defines a bot module that will receive all
    the message sent on the chatroom and call answer
    on it. Be careful with those modules"""

    def __init__(self, bot, name, desc) :
        BotModule.__init__(self, bot, desc)
        self.name = name

    def is_concerned(self, command) :
        return True
