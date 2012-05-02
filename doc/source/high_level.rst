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
