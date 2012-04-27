# -*- coding: utf-8 -*-

class ConfigException(Exception):
    """ A general exception raised when the configuration file is not valid """

    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return self.desc
