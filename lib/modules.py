#! /usr/bin/env python2
#-*- coding: utf-8 -*-

import threading

def answercmd(f) :
    pass

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

    def do_answer(sender, mess) :
        cmd = msg_body.split(" ")[0]
        if not self.is_concerned(cmd) :
            return

        if mess.getType() == "chat" and not self.pm_allowed :
            try :
                #Calling the 'answer" method of the module
                send = self.answer(sender, text_msg)

                #If the method is just a string, it will be the bot's answer
                if type(send) == str or type(send) == unicode:
                    bot.say(send, in_reply_to=mess)

                #If it's a list we display each message with a time delay
                elif type(send) == list:
                    for line in send:
                        time.sleep(0.3)
                        bot.say(line, in_reply_to=mess)
                        
                #If it's a dictionary, it is {"text": raw_message,    # Text message, transform XHTML if empty
                #                             "xhtml" : xhtml_message # XHTML message
                #                             "monospace" : True      # XHTML message is the text with monospace
                #                             "users" : { "pseudo1" : {...} } # Send the same type of dictionnary
                #                                                               in private to the users
                #                            }
                elif type(send) == dict:
                   self._dict_messages(send)

                else:
                    #In any other case, an error has occured in the module
                    if send is not None:
                        self.say(_("Error from module %s : %s") % (classe.command, send))
            except:
                self.say(_("Error !"))
                logger.error(_("Error from module %s : %s") % (classe.command, traceback.format_exc()))

    def _dict_messages(self, send, priv=None) :
        if "xhtml" in send and "text" in send:
            bot.say_xhtml(send["text"], send["xhtml"], priv=priv, in_reply_to=mess)
        elif "text" in send and "monospace" in send and send["monospace"]:
            html_msg = send["text"]
            html_msg = html_msg.replace("&", "&amp;")
            html_msg = html_msg.replace("<", "&lt;")
            html_msg = html_msg.replace(">", "&gt;")
            html_msg = '<p><span style="font-family: monospace">%s</span></p>' % html_msg.replace("\n", "<br/>\n") 
            #TODO others characters to convert ?
            bot.say_xhtml(send["text"], html_msg, priv=priv, in_reply_to=mess)
        else:
            bot.say(send["text"], priv=priv, in_reply_to = mess)

        if "users" in send :
            for user, send_user in send["users"] :
                self._dict_messages(send_user, priv=user)


class SyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command. This is the most common case """

    def __init__(self, bot, desc, command, pm_allowed=True) :
        BotModule.__init__(self, bot, desc)

        self.command = command
        self.pm_allowed = pm_allowed
    
    def is_concerned(self, command) :
        return command == self.command

    def answer(self, sender, args) :
        return "To be implemented"

class MultiSyncModule(BotModule) :
    """ Defines a bot module that will answer/execute an action
    after a command defined in a list. """

    def __init__(self, bot, commands, pm_allowed=True) :
        BotModule.__init__(self, bot, desc)

        self.commands = commands
        self.pm_allowed = pm_allowed

    def is_concerned(self, command) :
        return command in self.command

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




