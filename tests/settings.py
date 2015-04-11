import os


os.environ.setdefault('DJANGO_SECRET_KEY', 'bad-key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///sqlite_database')

from mozy.settings import *  # NOQA
