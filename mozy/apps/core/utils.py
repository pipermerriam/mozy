import os
import datetime


def generic_upload_to(instance, filename):
    """
    Generic `upload_to` function for models.FileField and models.ImageField
    which uploads files to `<app_label>/<module_name>/<file_name>`.
    """
    now = datetime.datetime.now()
    return os.path.join(
        instance._meta.app_label,
        instance._meta.model_name,
        now.strftime('%Y'),
        now.strftime('%m'),
        now.strftime('%d'),
        filename,
    )
