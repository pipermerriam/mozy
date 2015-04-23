import os


os.environ.setdefault('DJANGO_SECRET_KEY', 'bad-key')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:@localhost:5432/mozy')
os.environ.setdefault('DJANGO_DEFAULT_FILE_STORAGE', 'inmemorystorage.InMemoryStorage')
os.environ.setdefault('DJANGO_STATICFILES_STORAGE', 'inmemorystorage.InMemoryStorage')

from mozy.settings import *  # NOQA
