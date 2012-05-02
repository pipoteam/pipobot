#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" This module provides necessary elements to use sqlalchemy
    in modules and create tables accordingly when the bot is
    initialized"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
