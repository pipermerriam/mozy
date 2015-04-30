from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.core.cache import cache
from django.utils.http import urlquote
from django.conf import settings
from django.utils.module_loading import import_string

from pipeline.storage import PipelineMixin

from s3_folder_storage.s3 import StaticStorage

from mozy.apps.mosaic.tasks import transfer_local_file_to_remote


def delegated_storage_method(method_name):
    def method(self, name, *args, **kwargs):
        backend_method = getattr(self.get_storage(name), method_name)
        return backend_method(name, *args, **kwargs)
    method.__name__ = method_name
    return method


class QueuedStorage(object):
    local_path = None
    local_options = None

    remote_path = None
    remote_options = None

    cache_prefix = 'QueuedStorage'

    def __init__(self,
                 local_path=None, remote_path=None,
                 local_options=None, remote_options=None,
                 cache_prefix=None):
        # local
        self._local = None
        self.local_path = local_path or self.local_path
        self.local_options = local_options or self.local_options or {}

        # remote
        self._remote = None
        self.remote_path = remote_path or self.remote_path
        self.remote_options = remote_options or self.remote_options or {}

        # cach
        self.cache_prefix = cache_prefix or self.cache_prefix

    def get_storage(self, name):
        """
        Returns the storage backend that should be used for the named resource.
        """
        cache_result = cache.get(self.get_cache_key(name))
        if cache_result:
            return self.remote
        elif cache_result is None and self.remote.exists(name):
            cache.set(self.get_cache_key(name), True)
            return self.remote
        else:
            return self.local

    @property
    def local(self):
        if self._local is None:
            self._local = import_string(self.local_path)(**self.local_options)
        return self._local

    @property
    def remote(self):
        if self._remote is None:
            self._remote = import_string(self.remote_path)(**self.remote_options)
        return self._remote

    def get_cache_key(self, name):
        """
        Returns the storage backend that should be used for the named resource.
        """
        return "{0}_{1}".format(self.cache_prefix, urlquote(name))

    def is_local(self, name):
        """
        Returns whether the named resource should use the local storage backend.
        """
        return self.get_storage(name) is self.local

    def is_remote(self, name):
        """
        Returns whether the named resource should use the remote storage backend.
        """
        return self.get_storage(name) is self.remote

    def transfer(self, local_name, cache_key=None):
        if cache_key is None:
            cache_key = self.get_cache_key(local_name)

        transfer_local_file_to_remote(
            name=local_name, cache_key=cache_key,
            local_path=self.local_path, local_options=self.local_options,
            remote_path=self.remote_path, remote_options=self.remote_options,
        )

    # core API
    def save(self, name, content, max_length=None):
        cache_key = self.get_cache_key(name)
        cache.set(cache_key, False)
        local_name = self.local.save(name, content)

        self.transfer(local_name, cache_key=cache_key)
        return local_name

    accessed_time = delegated_storage_method('accessed_time')
    created_time = delegated_storage_method('created_time')
    modified_time = delegated_storage_method('modified_time')
    delete = delegated_storage_method('delete')
    exists = delegated_storage_method('exists')
    get_available_name = delegated_storage_method('get_available_name')
    get_valid_name = delegated_storage_method('get_valid_name')
    list_dir = delegated_storage_method('list_dir')
    open = delegated_storage_method('open')
    path = delegated_storage_method('path')
    size = delegated_storage_method('size')
    url = delegated_storage_method('url')


class S3PipelineStorage(PipelineMixin, ManifestFilesMixin, StaticStorage):
    pass


from s3_folder_storage.s3 import DefaultStorage


class S3DefaultStorage(DefaultStorage):
    preload_metadata = False


class QueuedDefaultStorage(QueuedStorage):
    local_path = 'django.core.files.storage.FileSystemStorage'
    remote_path = 's3_folder_storage.s3.DefaultStorage'
    remote_options = {
        'preload_metadata': False,
    }
