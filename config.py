# coding: utf-8
import os

DEBUG = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'mysql://unitcostdatabase:unitcostdatabase@localhost/unitcostdatabase'
WHOOSH_BASE = os.path.join(os.path.dirname(__file__), 'search.db')
