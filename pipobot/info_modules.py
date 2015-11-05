# -*- coding: utf-8 -*-

from __future__ import print_function

import re
from glob import glob
from importlib import import_module
from inspect import getmembers, isclass
from os import chdir, environ, walk
from os.path import exists, isdir, join
from sys import builtin_module_names, path, version_info
from pathlib import Path

IMPORTS = re.compile('^\s*import\s+(\S+)\s*$|^\s*from\s+(\S+)\s+import\s+')
BUILTINS = set(builtin_module_names) | set(dir(__builtins__))
MODULE_TYPES = ['SyncModule', 'MultiSyncModule', 'ASyncModule', 'ListenModule', 'PresenceModule', 'IQModule', 'NotifyModule']
PATHS = list(path)
VIRTUAL_ENV = environ.get('VIRTUAL_ENV', None)
if VIRTUAL_ENV:
    PATHS += "%s/lib/python%i.%i/site-packages" % (VIRTUAL_ENV, version_info[0], version_info[1])


def is_external(package):
    if 'pipobot' in package or package in BUILTINS:
        return False
    for prefix in PATHS:
        package_path = "/".join((prefix, package.split(".")[0]))
        if (exists(package_path + ".py") or glob(package_path + "*.so") or (exists(package_path) and isdir(package_path))):
            if "site-packages" in prefix or "dist-packages" in prefix:
                return True
            if "python2" in prefix.lower() or "python3" in prefix.lower():
                return False
    return True


def is_in_module(path):
    return exists(path + '.py') or isdir(path) and exists(join(path, '__init__.py'))


def info_modules(bot, module_paths):
    for module_path in module_paths:
        chdir(module_path)
        pipobot_modules = sorted(path for path in Path('.').iterdir() if path.is_dir() and (path / '__init__.py').is_file())

        with open('info_modules.md', 'w') as md:
            for path in pipobot_modules:
                print('#',  path, file=md)

                externals = set()
                for root, filename in [(r, f) for r, _, files in walk(str(path)) for f in files if f.endswith('.py')]:
                    with Path(root, filename).open() as f:
                        mod = set(next(i for i in m.groups() if i is not None).split('.')[0] for l in f for m in IMPORTS.finditer(l))
                        externals |= set(m for m in mod if not is_in_module(join(root, m)) and is_external(m))

                if externals:
                    print('depends:', file=md)
                    for external in externals:
                        print('*', external, file=md)
                    print(file=md)

                try:
                    module = import_module(str(path))
                    for name, member in getmembers(module, isclass):
                        if hasattr(member, 'mro') and member.mro()[1].__name__ in MODULE_TYPES and name not in MODULE_TYPES:
                            print('%s:' % name, file=md)
                            print(file=md)
                            desc = member(bot).desc
                            if isinstance(desc, dict):
                                if '' in desc:
                                    print(desc[''], file=md)
                                    print(file=md)
                                print('|Command|Description|', file=md)
                                print('|-------|-----------|', file=md)
                                for key, value in desc.items():
                                    if key:
                                        print('|%s|%s|' % (key, value), file=md)
                                print(file=md)
                            else:
                                print('```\n%s\n```\n' % desc, file=md)
                except Exception as e:
                    print(':exclamation: import failed: %s' % e.message, file=md)
                print(file=md)
