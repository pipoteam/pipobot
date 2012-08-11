# -*- coding: utf8 -*-

"""
Internationalisation and translation functions.
"""

from os.path import dirname, join
import gettext
import logging


LOGGER = logging.getLogger("translation")


def setup_i18n(lang):
    """
    Initialises the gettext infrastructure using the specified language.
    """

    LOGGER.debug("Initialising i18n")

    base_path = join(dirname(__file__), "i18n")

    if lang.startswith('en'):
        trans = gettext.NullTranslations()
    else:
        try:
            trans = gettext.translation('pipobot', base_path, languages=[lang])
        except IOError:
            LOGGER.error("Unable to load translations for language ‘%s’, "
                "disabling translations.", lang)
            trans = gettext.NullTranslations()

    trans.install(unicode=True, names=['gettext', 'ngettext'])

# When install() is called on a gettext translations object, the functions “_”,
# “gettext”, and “ngettext” are added to __builtins__ so they are available to
# every module without needing to import anything.
# We also add _N (the translation marker) to the builtins as soon as this
# module is loaded so it can be used to translate string in modules loaded
# afterwards.

import __builtin__
__builtin__.__dict__['_N'] = lambda text : text