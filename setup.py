from setuptools import setup, find_packages
import os

from pipobot import __version__

def list_all_data_files(dst_path, src_path):
    f = []
    for (dirpath, dirname, filenames) in os.walk(src_path):
        f.append((os.path.join(dst_path, dirpath),
                  [os.path.join(dirpath, filename) for filename in filenames]))
    return f

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

    entry_points = {
        'console_scripts' : [
            'pipobot = pipobot.bot:main',
        ]
    },

    install_requires=['distribute'],
    requires=['BeautifulSoup'],
)
