Architecture of a module
========================

To create a new module for `pipobot` you have to write some python classes
which are subclasses of pre-defined type of modules.
See below for the description of all different modules.
A classic structure of a module (here `date`) is : ::

    modules/date/
         __init__.py
         cmd_date.py

``cmd_date.py`` will contain the `CmdDate` class defining the command.
``__init__.py`` will just have to contain 'from cmd_date import CmdDate' so
importing modules.date will result to the import of the command class.
You can add as many cmd_[name].py as your module requires commands. You 
just have to import them all in ``__init__.py``.

Types of modules
----------------

There are several classes of modules, depending on what you are trying to achieve.

SyncModule
^^^^^^^^^^

A *SyncModule* is a module that can be called *explicitly* by a user
(Sync stands for Synchronous). It can be used in a room like this : ::

    <user> !date
    <bot> Today is `insert the date of the day here !`

For more details, see :ref:`sync_module`.


MultiSyncModule
^^^^^^^^^^^^^^^

A *MultiSyncModule* is very similar to a *SyncModule* is very similar to a SyncModule, 
except that one *MultiSyncModule* can handle several commands in it.
This is quite useful when commands are very simple, and does not require python code to 
be handled.

For more details, see :ref:`multisync_module`.

AsyncModule
^^^^^^^^^^^

An *AsyncModule* is a module which is not related to anything said in the room.
For instance, it could be a module announcing the hour every hour, or analysing mails
from a mail server and announcing new messages in the room.

For more details, see :ref:`async_module`.

ListenModule
^^^^^^^^^^^^

A *ListenModule* is a module where the bot reacts to something that has been
said in the room, but without an explicit call of a command, as in : ::

    <user> Here is an awesome link : http://pipobot.xouillet.info !
    <bot> [Lien] Titre : Forge xouillet

Every message in a room can be analysed by the bot, and he can react if the message 
matches some criteria (contains a URL for instance).

For more details, see :ref:`listen_module`.

PresenceModule
^^^^^^^^^^^^^^

A *PresenceModule* reacts to every presence message in a room, for instance joins and leaves
of users.
For instance: ::

    *** user has joined the room
    <bot> user: welcome to the room !!

For more details, see :ref:`presence_module`, or the :ref:`users_module` which is a *PresenceModule*.

What they can return
--------------------

A string
^^^^^^^^

If a module returns a string, the bot will simply say it in the room.

A list of strings
^^^^^^^^^^^^^^^^^

If a module returns a list of string, the bot will say each element of 
the list one after the other.
Example:

.. code-block:: python

    def some_function(self, sender, message):
        return ["msg1", "msg2", "msg3"]

will result to: ::

    <bot> msg1
    <bot> msg2
    <bot> msg3


A dictionary
^^^^^^^^^^^^

Thanks to  `XEP-0071 <http://xmpp.org/extensions/xep-0071.html>`_, XMPP protocols allows
to send XHTML messages for clients that support it.
If you want your module to send XHTML messages, you can make it return a dictionary like : ::

    return {"text" : "*Message for clients which don't support XHTML*", 
            "xhtml" : "<b>Message for clients which do support XHTML</b>"
            }

Some clients do not handle monospace fonts, so if you want to had some presentation in your messages
(tabulars for instance) they will not render correctly. If those clients support XHTML messages, you
can create an XHTML message that will do it :
    
.. code-block:: python

    raw_msg =  "| Some       | tabular   |\n"
    raw_msg += "| requiring  | monospace |"
    return {"text" : raw_msg, 
            "monospace" : True}

The following XHTML message will be automatically created and sent :

.. code-block:: html

    <p>
        <span style="font-family: monospace">
            | Some       | tabular   | <br />
            | requiring  | monospace |
        </span>
    </p>
    

Finally, dictionaries can be used to send private message to several users.
Example:

.. code-block:: python

    return { "user1" : { "text": "Message for user1", 
                         "monospace": True }, 
             "user2" : { "text" : "raw message for user2", 
                         "xhtml" : "<p> an <b> XHTML </b> message for user2 </p>"}
            }

Nothing, None or ""
^^^^^^^^^^^^^^^^^^^

If a module has no return statement, returns None or "", then
the bot will simply not say anything.

Using configuration parameters
------------------------------

Some modules may require configuration parameters that will be provided
by the ``pipobot``'s main configuration file.

``pipobot`` includes a syntax to define such parameters, and will automatically: 

    * check if required parameters are present
    * replace optional parameters by a default value
    * check if provided parameters are correct (type verification)

To add parameters to a module you must provide a `_config` attribute to the module 
class, listing them.
For example if we want a module to parse the several sample of configuration: ::

    modules_config:
        my_module:
            param1: True
            param2:
                - foo
                - bar
            param3: 
                key1: val1
                key2: val2
            # OPTIONAL
            param4: "somestring"

In the corresponding module class we will add:  ::

    class MyModule(SyncModule):
        _config = (("param1", bool, None), ("param2", list, None),
                   ("param2", dict, None), ("param4", string, "somestring))

Then in the code of the module we will be able to access to these parameters with `self.param1`, `self.param2`...

Possible types of parameters are defined by the yaml language: 
    * a boolean
    * a string
    * an int
    * a list
    * a dictionary 

Each element of the _config array is a parameter constructed with (name, type, default_value), None in default_value meaning
that the parameter is not optional.


Specific description of modules
===============================

.. _modules_presentation:
.. _sync_module:

SyncModule
----------

Definition of module
^^^^^^^^^^^^^^^^^^^^

A *SyncModule* is a module that can be called *explicitly* by a user
(Sync stands for Synchronous). It can be used in a room like this : ::

    <user> !date
    <bot> Today is `insert the date of the day here !`

Some parameters must be specified to define a command :
    - *command* : its name (`date` in the previous example)
    - *desc* : a description of the module which will be used by the `help` module (see :ref:`desc_syntax`.)

Writing handlers
^^^^^^^^^^^^^^^^

*SyncModule* mother class implements a parsing method for commands.
For instance a command can take several subcommands as in this example: ::

    <user> !todo
    <bot> This is a command to handle TODO-list
    <user> !todo list
    <bot> Here is the list of all TODO : …
    <user> !todo add some_list I have TODO this !
    <bot> The todo 'I have TODO this !' has been successfully added to 'some_list'

*list* and *add* are subcommands for the main **todo** command.
To each subcommand you want to define, you have to write a handler
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

        @defaultcmd
        def default(self, sender, message):
            #In any other case this will be called
            pass

The ``@defaultcmd`` decorator specify the method that will be called when *no other method* corresponds
to user's input.
For instance in this example, all these calls will be handled by the `default` method: ::

    !todo
    !todo should RTFM
    !todo don't know what i am doing

This behaviour is interesting if you want to handle errors yourself : any use of the command that is not conform
to the syntax defined by other decorators will be handled by the ``default`` method.

Finally you can use regular expressions in decorators to filter subcommands differently.
For instance we can re-write the **todo** module like this:

.. code-block:: python
    
    class CmdTodo(SyncModule):
        def __init__(self, bot):
            pass

        @answercmd("^$")
        def empty(self, sender, args):
            pass

        @answercmd("list"):
        def list(self, sender, args):
            pass

        @answercmd("add (?P<list_name>\S+) (?P<desc>.*)"=
        def add(self, sender, args):
            liste = args.group("list_name")
            desc = args.group("desc")

        @answercmd("(remove|delete) (?P<ids>(\d+,?)+)")
        def remove(self, sender, args):
            ids = args.group("ids").split(",")

As you can see in this example, with this syntax you can do a lot of work to filter commands directly in the
decorator.
In the previous example, a call like : ::

!todo add somelist a new todo to add

will be handled by the ``add`` method, and a call like : ::

!todo remove 1,2,3

will be handled by the ``remove`` method.

Empty call like : ::

!todo

will be handled by the ``empty`` method.

Finally any other syntax will raise an error so the bot will return a message recommending to read
the manual of the command since no ``@defaultcmd`` is provided.

You can use in a given module regular expression-based decorators and "classic" decorators.
Just be careful of the behaviour if for instance some regular expressions are to permissive.

*WARNING*: Be careful not to use too permissive pattern in ``@answercmd`` decorator.
For instance if you use this set of decorators :

.. code-block:: python

    @anwsercmd("add (?P<list_name>\S+) (?P<desc>.*)")
    @answercmd("search (?P<query>.*)")
    @answercmd("(remove|delete) (?P<ids>(\d+,?)+)")
    @answercmd("")

*ANY* call to the corresponding command will be caught by the last one since an empty regular
expression matches *a lot* of things !!
If you want to define the `empty` subcommand, just use ``@answercmd("^$")``.

.. _multisync_module:

MultiSyncModule
---------------

A *MultiSyncModule* is similar to a *SyncModule* but it contains several commands which will be handled
by the same module. You initialize it with a dictionary command_name → command_description.
Then you will provide some handling method with the same syntax as you would in a *SyncModule*.

.. _async_module:

AsyncModule
-----------

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
------------

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
--------------

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

Some internal modules
=====================


Help Module
-----------

.. _desc_syntax:

Description format
^^^^^^^^^^^^^^^^^^

.. _users_module:

User Monitoring Module
----------------------

.. _high_level:

High-Level Modules
==================

These modules are derived from ``general`` module presented here : :ref:`modules_presentation`.
They exist to simplify writing some modules executing similar tasks.

FortuneModule
-------------

This module is a ``SyncModule`` with some pre-defined functions.
It can be used in this context : you have a website presenting some quote/fortunes and you want
to write a module which, when called, will parse quotes from the website and return it.
In addition to all ``SyncModule`` parameters, it has two more attributes you have to set :
``url_random`` and ``url_indexed``.
It provides commands with the syntax: ::

    !cmd
    !cmd some_number

In the first case, the module will use the ``url_random``, and parse it.
In the second case, the module will use the ``url_indexed``, insert in it ``some_number``, and get the
corresponding page.
All you need to do in your module is to override the ``extract_data``, method using with your own, using
the ``soup`` parameter which is a BeautifulSoup object created with the content of the page.

You can see some example of such ``FortuneModule`` in the bot (bashfr, vdm, chuck, …).

NotifyModule
------------

This module is the combination of a ``SyncModule`` and an ``AsyncModule``.
You have to define a ``do_action`` method that will be called every `n` seconds.
In a ``NotifyModule``, the ``action`` method (see :ref:`async_module` for more details) is already defined
and will check if the module has been `muted` or not. If it has not, the method ``do_action`` that you are
supposed to write will be called.
The ``NotifyModule`` will provide a ``mute/unmute`` method that will disable/enable the notifications.
You can add to it as many ``@answercmd`` as you need to, like in any other ``SyncModule``.

The ``reminder`` module is an example of such module.
