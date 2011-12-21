Architecture of a module
------------------------

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
