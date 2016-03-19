Pipobot
=======
Pipobot is a modular bot for jabber MUCs.

Its documentation hosted on [Read the Docs](https://pipobot.readthedocs.org/en/latest/)

Quickstart
==========

Dependencies
------------
Pipobot is written in python and compatible with versions of python2>=2.5.

It is based on these Python modules:

    - `python-sleekxmpp`: engine of connection to XMPP servers
    - `python-yaml`: configuration files are yaml files
    - `python-sqlalchemy`: Pipobot is storing data to database through sqlalchemy library.

Invoking the bot from repository
--------------------------------

You need to create a configuration file for the bot. An example of such file is provided in
the `pipobot.conf.yml`.
To start the bot, you just have to use the command :

`python -m pipobot /path/to/the/config_file.yml`

Default configuration file used is /etc/pipobot.conf.yml

Deploying the bot
-----------------
You can use setup.py script to install pipobot on your system.
`python setup.py install`

Then start it with the command `pipobot`.
You can also set it to start in background by using the `-b` option.

Alternatively, package creation files are provided for archlinux and debian.
You can find these files in the distrib/ directory.
