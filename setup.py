#!/usr/bin/env python2

from setuptools import setup
from os.path import dirname, join, isdir, splitext
import os
import sys

try:
    from babel.messages import frontend as babel
except ImportError:
    sys.stderr.write("The babel module is not installed. Translation tools "
                     "will not be available.\n")
    babel = None

try:
    from sphinx.setup_command import BuildDoc as build_doc
except ImportError:
    sys.stderr.write("The sphinx module is not installed. Documentation generation "
                     "will not be available.\n")
    build_doc = None


if sys.hexversion < 0x02060000:
    sys.stderr.write(
        "This program require Python 2.6 or newer"
    )
    sys.exit(1)


if __name__ == '__main__':
    # We cannot import pipobot._version directly since we could get an already
    # installed version.

    filename = join(dirname(__file__), 'pipobot', '_version.py')

    with open(filename) as f:
        code = compile(f.read(), "_version.py", 'exec')
        exec(code, globals(), locals())
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
        kwargs['cmdclass'] = {}

    if build_doc:
        kwargs['cmdclass']['build_sphinx'] = build_doc

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
