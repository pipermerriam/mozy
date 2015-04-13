from django.conf import settings
from django.utils.module_loading import import_string


def get_mosaic_backend(backend_class=None):
    if backend_class is None:
        backend_class = settings.MOSAIC_BACKEND
    return import_string(backend_class)
