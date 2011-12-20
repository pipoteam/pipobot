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

.. _async_module:

AsyncModule
===========

.. _listen_module:

ListenModule
============

.. _presence_module:

PresenceModule
==============
