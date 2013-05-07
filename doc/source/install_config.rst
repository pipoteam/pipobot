Presentation
------------

Requirements
------------

Configuration
-------------

Pipobot configuration is centralized in a single yaml file. In this file you will configure *global* parameters, select rooms
the bot will join, choose modules to use and configure them.
An example of such file is distributed with pipobot under the name of `pipobot.conf.yml`. You can find in it a full example of
configuration and can refer to it for syntax questions.
In this documentation we will develop parameters you can use and what they mean.

Config section
++++++++++++++

In this section you will have to provide general parameters for pipobot, eg parameters independent of rooms and modules.
Here is a list of parameters you can use:

    * logpath: a *relative or absolute path* to a log file for pipobot
    * xmpp_logpath: a *relative or absolute* path to log all debug related to XMPP communication. This will only be useful
      in debug mode otherwise nothing will be logged (see :ref:`command_line_args`).
    * force_ipv4: the bot will try to connect to the XMPP server in IPv6 (if a DNS record exists) if this *boolean* is not provided.
    * lang: the language the application will use
    * modules_path: a *list* of directories (relative or absolute) where the bot will try to find modules.

Database section
++++++++++++++++

Configuration of the database which will be used by the bot.
Supported engines are: *MySQL*, *PostgreSQL*, *SQLite*, with their respecting configuration.

SQLite configuration
^^^^^^^^^^^^^^^^^^^^
These parameters are required with this engine:

    * engine: must be *sqlite*
    * src: a relative or absolute path to a file where the database will be stored

MySQL or PostgreSQL configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For those engines here are the required parameters:

    * engine: *mysql* or *postgresql*
    * user: username to access the database
    * password: password to access the database
    * host: the server where the database is hosted (can be hostname or IP)
    * name: the name of the database on the server


Room section
++++++++++++

A room is a reference to an XMPP MUC that the bot will join.
It requires these parameters:

    * chat: the MUC it will join (room@domain.tld).
    * login: the JID used to authenticate to an XMPP server.
    * passwd: the password used for the authentication.
    * resource: the resource of the bot
    * nick: the nickname of the bot in the MUC
    * modules: a list of modules or groups to load for this room. Groups must be prefixed with an underscore.

Group section
+++++++++++++

A group is a list of modules we create that can be referenced in a room configuration (see the Room section above).
Example:

groups:
    group1:
        - module1
        - module2
    group2:
        - module1
        - module3

Then in the *modules* parameter of a room can add `_group1` or `_group2`.

Module-config section
+++++++++++++++++++++

In the *module_config* section you will define modules specific configuration.
You can refer to the documentation of these modules to determine how to configure them, or if there is no such documentation
to messages given by the bot when it is started: it will inform you that some configuration parameters are missing, or what
default parameters are used instead.

Modules configuration are defined this way:

    module_config:
        module_name:

            param1: a single value

            param2:
                - a list
                - of items

            param3:
                key: value


.. _test_config:

Testing section
+++++++++++++++

The *testing* section is what will define which parameters and which modules the bot will use when started in testing modes
(see :ref:`unit_test_mode`).
You will need to provide these parameters:

    * fake_nick: a nickname for the bot.
    * fake_chan: a fake chan name (like XMPP MUC name).
    * modules: a list of modules, just like in a real room.


Invocation
----------

`pipobot` can be started in serveral modes:
    - *XMPP* mode : this is the principal mode for the bot : it will connect to a Jabber MUC and start listening for commands.
    - *Testing* modes : they do not require an XMPP server : they are provided in order to easily test modules and bot functionalities.

.. _command_line_args:

General command-line options
++++++++++++++++++++++++++++

When you start the bot in *XMPP* mode, you can use these options (use ``pipobot -h`` to retrieve them): ::

  --version         show program's version number and exit
  -h, --help        show this help message and exit
  -q, --quiet       Log and print only critical information
  -d, --debug       Log and print debug messages
  -b, --background  Run in background, with reduced privileges
  --pid=PID_FILE    Specify a PID file (only used in background mode)

You can also always specify a configuration file (default being /etc/pipobot.conf.yml): ::

    pipobot /path/to/alternative/config

Check-modules mode
++++++++++++++++++

In this mode the bot will only check the configuration file, check all modules and verify that
you provided all required configuration parameters.

To use this mode use: ::

  --check-modules   Checks if modules' configuration is correct

.. _unit_test_mode:

Unit-test mode
++++++++++++++

In this mode, unit test modules will be used and started to detect errors.
It will use the ``testing`` section of the configuration file (see :ref:`test_config`).

If you want to learn more about unit test, you can refer to :ref:`unit_test`.

To use this mode use: ::

  --unit-test       Run unit test defined in the config file

Example: ::

    pipobot --unit-test

    test_todo_add (todo.TodoAdd)
    !todo add ... ok
    test_todo_remove (todo.TodoRemove)
    !todo remove ... ok
    test_search (todo.TodoSearch)
    !todo search ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 1.054s

    OK

Script mode
+++++++++++

This mode allows you to start the bot with a pre-defined list of commands.
Commands are separated with a *;*.
It will generate their outputs and display them to you.
Example: ::

    pipobot --script=":help;http://www.google.fr;:todo list all"

    --> :help
    <== I can execute:
    -todo
    --> http://www.google.fr
    <== [Lien] Titre : Google
    --> :todo list all
    <== TODO-list vide

Interactive mode
++++++++++++++++

This mode is provided to simulate an XMPP room locally.
You can start the bot in this mode with: ::

    pipobot --interract

Loaded modules will be those defined in the ``testing`` section of the configuration file (see :ref:`test_config`).
This will start a server waiting for fake XMPP clients to connect.
To create a new client you can use the **pipobot-twisted** provided application: ::

    pipobot-twisted foo

This will create a new client called `foo` connecting to the fake server. You can then enter your commands
and see the result : ::

    pipobot-twisted foo

    Connected to server
    Welcome !
    *** foo has joined
    !help
    <foo> !help
    <Pipo-test> I can execute:
    -todo
    !todo add liste un test
    <foo> !todo add my_list a test
    <Pipo-test> TODO added
    !todo list
    <foo> !todo list
    <Pipo-test> All TODO-lists:
    my_list
    !todo list my_list
    <foo> !todo list my_list
    <Pipo-test> my_list :
    1 - a test (by foo on 2012/03/10 at 16:20)

You can start multiple client to the room as long as they have different nicknames.
