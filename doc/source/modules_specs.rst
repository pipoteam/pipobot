.. _sync_module:

SyncModule
==========

Definition of module
--------------------

A *SyncModule* is a module that can be called *explicitly* by a user
(Sync stands for Synchronous). It can be used in a room like this : ::

    <user> !date
    <bot> Today is `insert the date of the day here !`

Some parameters must be specified to define a command :
    - *command* : its name (`date` in the previous example)
    - *desc* : a description of the module which will be used by the `help` module (see :ref:`desc_syntax`.)

Writing handlers
----------------

*SyncModule* mother class implements a parsing method for commands.
For instance a command can take several subcommands as in this example: ::

    <user> !todo
    <bot> This is a command to handle TODO-list
    <user> !todo list
    <bot> Here is the list of all TODO : …
    <user> !todo add some_list I have TODO this !
    <bot> The todo 'I have TODO this !' has been successfully added to 'some_list'

*list* and *add* are subcommands for the main **todo** command.
The first call with no arguments will be referenced as *default* subcommand.
To each subcommand you want to define, you have to write add a handler 
to the module class.

A handler is a Python method with this signature: ::
    
    def some_name(self, sender, message):

The parameters are :
    - `sender` is the name of the user who sent the command (`user` in the previous example).
    - `message` is what the user sent, without the command name and the subcommand name.

For instance in: ::

    <user> !todo add some_list I have TODO this !
    
`sender` will be *user* and `message` will be *some_list I have TODO this !*.

In order to define a subcommand, you have to add a descriptor to the method you write.
It can be ``@defaultcmd`` or ``@answercmd("subcommand1", "subcommand2")``.
For instance the skeleton of the **todo** module will be:

.. code-block:: python

    from lib.modules import SyncModule, answercmd, defaultcmd

    class CmdTodo(SyncModule):
        def __init__(self, bot):
            desc = "A TODO module"
            command_name = "todo"
            SyncModule.__init__(self, bot, desc, command_name)

        @defaultcmd
        def default(self, sender, message):
            #what to do with !todo
            pass

        @answercmd("add")
        def add(self, sender, args):
            #what to do with !todo add some other args
            pass

        @answercmd("list")
        def list(self, sender, args):
            #what to do with !todo list some other args
            pass
         
        @answercmd("rm", "del")
        def rm(self, sender, args):
            #what to do with !todo rm or !todo del  some other args
            pass
    

.. _multisync_module:

MultiSyncModule
===============

A *MultiSyncModule* is similar to a *SyncModule* but it contains several commands which will be handled
by the same module. You initialize it with a dictionary command_name → command_description.
Then you will provide some handling method with the same syntax as you would in a *SyncModule*.

.. _async_module:

AsyncModule
===========

An *AsyncModule* is a module executing a task automatically every `n` seconds and send a message in a room
with the result of this task. Its action is not related to anything said in the room.

Example::

    <bot> You have received a new mail !!!

Additionally to the name and the description of the module (see :ref:`desc_syntax`) you have to provide a
`delay` which means : every `delay` seconds the action will be executed.
Then you write an `action` function with no argument :

.. code-block:: python

    def action(self):
        #some_work
        self.bot.say("The message we send to the room")

`action` is the method that will be called every `delay` seconds.

.. _listen_module:

ListenModule
============

An *ListenModule* is a module executing a task which depend on something that has been said in the room.
But as opposed to *SyncModule* it is not explicitly called with a `!command` syntax.

For instance, it can be used to analyse messages with URL : ::

    <user> hey, check this amazing link : http://www.nojhan.net/geekscottes/strips/geekscottes_103.png
    <bot> [Lien] Type: image/png, Taille : 68270 octets

The parameters required for a *ListenModule* are:

    * its name
    * a description (see :ref:`desc_syntax`)

The `answer` handler function will have this signature:

.. code-block:: python

    def answer(self, sender, message):
        #some work on the message
        if (re.findall(SOME_URL_REGEXP, message)):
            #handle url
            return "[Lien] Type: %s, Taille : %s octets" % (ctype, clength))
        else:
            return None

Then if the message contains an URL you can extract it, work on it and return some information about it.
If it does not, you return `None` so the bot will not say anything in the room.

.. _presence_module:

PresenceModule
==============

A *PresenceModule* is handling XMPP Presence stanza, for instance in a MUC : an user joins/leaves the room.
The handling method is named `do_answer` with this signature:

.. code-block:: python

    def do_answer(self, message):
        # some work on the message
        if join_message:
            self.bot.say("Hello %s !" % username)

Which will result in: ::

    *** user has joined
    <bot> Hello user !!!
