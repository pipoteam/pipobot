#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import checker
import ihm

if __name__ == "__main__":
    pass
else:
    from .. import register
    register(__name__, checker.AsyncReminder)
    register(__name__, ihm.CmdReminder)

