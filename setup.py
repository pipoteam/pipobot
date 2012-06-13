from setuptools import setup, find_packages
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build

import os
import sys

sys.path.insert(0, 'translation')
import msgfmt

from pipobot import __version__

def list_all_data_files(dst_path, src_path):
    f = []
    for (dirpath, dirname, filenames) in os.walk(src_path):
        f.append((os.path.join(dst_path, dirpath),
                  [os.path.join(dirpath, filename) for filename in filenames]))
    return f

# Class for compiling .po files
class build_trans(cmd.Command):
    description = 'Compile .po files into .mo files'
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        po_dir = os.path.join(os.path.dirname(os.curdir), 'translation', 'po')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:len(f) - 3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join('build', 'locale', lang, 'LC_MESSAGES')
                    dest = os.path.join(dest_path, 'pipobot.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if not os.path.exists(dest):
                        print 'Compiling %s' % src
                        msgfmt.make(src, dest)
                    else:
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime > dest_mtime:
                            print 'Compiling %s' % src
                            msgfmt.make(src, dest)

# Add the translation build to the default build
class build(_build):
    sub_commands = _build.sub_commands + [('build_trans', None)]
    def run(self):
        _build.run(self)

# Idem for install commands
class install_data(_install_data):

    def run(self):
        for lang in os.listdir('build/locale/'):
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'pipobot.mo')
            self.data_files.append( (lang_dir, [lang_file]) )
        _install_data.run(self)

# Put them in a nice dic
cmdclass = {
    'build': build,
    'build_trans': build_trans,
    'install_data': install_data,
}

setup(
    name = 'pipobot',
    version = __version__,
    description = 'A modular bot for Jabber MUCs',
    author = 'Pipoteam',
    author_email = 'pipoteam@xouillet.info',
#   url = '',

    packages = find_packages(exclude=["modules*"]),
    data_files = list_all_data_files('/usr/share/pipobot', 'modules'),
#   scripts = [],
    cmdclass = cmdclass,

    entry_points = {
        'console_scripts' : [
            'pipobot = pipobot.bot:main',
        ]
    },

    install_requires=['distribute'],
    requires=['BeautifulSoup'],
)
