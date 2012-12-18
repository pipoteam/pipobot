#!/usr/bin/env python2

from distutils.core import setup
from os.path import dirname, join, isdir, splitext
from sphinx.setup_command import BuildDoc
import os
import sys

try:
    from babel.messages import frontend as babel
except ImportError:
    sys.stderr.write("The babel module is not installed. Translation tools "
                     "will not be available.\n")
    babel = None

if sys.hexversion < 0x02060000 or sys.hexversion >= 0x03000000:
    sys.stderr.write(
        "This program require Python 2.6 or newer, but is not yet compatible "
        "with Python 3.\n"
    )
    sys.exit(1)


if __name__ == '__main__':
    # We cannot import pipobot._version directly since we could get an already
    # installed version.

    execfile(join(dirname(__file__), 'pipobot', '_version.py'))
    # __version__ is now defined.

    kwargs = {}
    if babel:
        kwargs['cmdclass'] = {
            'compile_catalog': babel.compile_catalog,
            'extract_messages': babel.extract_messages,
            'init_catalog': babel.init_catalog,
            'update_catalog': babel.update_catalog,
        }
    else:
        cmdclass = {}
    
    kwargs['cmdclass']['build_sphinx'] = BuildDoc

    packages = ['pipobot', 'pipobot.lib']
    data_files = ["i18n/*/LC_MESSAGES/pipobot.mo"]

    setup(
        name="PipoBot",
        version=__version__,
        description="A modular bot for Jabber MUCs.",
        author="Pipoteam",
        author_email="pipoteam@xouillet.info",
        url="http://github.com/pipoteam/pipobot",
        packages=packages,
        package_data={'pipobot': data_files},
        data_files=[('/etc', ['pipobot.conf.yml'])],
        requires=['yaml', 'sqlalchemy'],
        scripts=['bin/pipobot', 'bin/pipobot-twisted'],
        **kwargs
    )
