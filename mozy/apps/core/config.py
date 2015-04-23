from boto.s3.connection import S3Connection

from django.apps import AppConfig
from django.conf import settings
from django.core.files.storage import (
    default_storage,
    get_storage_class,
)


class MozyConfig(AppConfig):
    name = 'mozy.apps.core'

    def ready(self):
        S3Connection.DefaultHost = settings.AWS_S3_HOST
        default_storage._wrapped = get_storage_class()()
