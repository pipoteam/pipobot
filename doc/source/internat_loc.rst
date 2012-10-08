Internationalisation
--------------------

Pipobot uses the `gettext` module for internationalisation purposes. You can
use the following functions to render your module translatable.

.. function:: gettext(string)
              _(string)

    These functions take a string in argument and return the translated string.
    Sample usage::

        self.bot.say(_("Hello, World!"))

    When one of these two functions are used, the string passed in parameter
    will be automatically proposed for translation.

    If you want to translate a string format, pass only the format to the
    function::
        self.bot.say(_("Hello, %s") % name)

    If you have more than one format parameter, it is better to name them
    explicitely because the translator may want to reverse the order::
        self.bot.say(_("Today is %(month)s, %(day)d") % {'month': month,
            'day': day})

.. function:: ngettext(singular, plural, n)

    ``ngettext`` is used to translate expressions which can be pluralised.
    Sample usage::
        self.bot.say(ngettext("You have %d message", "You have %d messages",
            message_count) % message_count)

    Always use ``ngettext`` instead of ``if message_count == 1: …`` because 
    some languages have pluralization rules different from English (for
    instance, in French, `0` is singular, not plural, and in Polish, there are
    5 different plural forms depending on the item count)

.. function:: N_(string)

    ``N_`` is a no-op. It just returns the string passed in parameter. It is
    used to mark strings which should be translatable but cannot be directly
    translated because the translation system is not already active (so ``_``,
    ``gettext`` and ``ngettext`` are unavailable). That may be the case for
    strings defined as constants in a Python module or as a class attribute.

    For instance::

        HELLO_MESSAGE = N_("Hello, World!")
        […]
        def say_hello():
            print _(HELLO_MESSAGE)

You do not need to ``import`` anything to use these functions: they are always
defined at the global level.

Translation handling
--------------------

Pipobot uses the ``babel`` module to handle translations. If you intend to add
new translations or update existing ones, you will need to install this module.

New language
^^^^^^^^^^^^

To translate Pipobot to a new language (for instance `zz_ZZ`, use the
following commands (from the directory containing the ``setup.py`` script)::
    python setup.py extract_messages # Extract the messages from Pipobot’s sources
    python setup.py init_catalog -l zz_ZZ # Create a translation catalog for the specified language

You can now edit ``pipobot/i18n/zz_ZZ/LC_MESSAGES/pipobot.po`` (with a standard
text editor or POEdit, for instance) and translate every message. When done,
run::
    python setup.py compile_catalog # Compile the translation catalog

The translation can now be used by Pipobot.


Update an existing language
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To update an existing translation catalog in order to take into account the
changes in Pipobot’s source code, run the following commands (replace `zz_ZZ`
with the name of the catalog you want to update)::
    python setup.py extract_messages # Extract the messages from Pipobot’s sources
    python setup.py update_catalog -l zz_ZZ # Update the translation catalog for the specified language

You can now edit ``pipobot/i18n/zz_ZZ/LC_MESSAGES/pipobot.po`` (with a standard
text editor or POEdit, for instance) and translate every message. When done,
run::
    python setup.py compile_catalog # Compile the translation catalog

The translation can now be used by Pipobot.
