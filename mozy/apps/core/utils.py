import os


def uuid_upload_to(instance, filename):
    """
    Expects a uuid as the filename.
    """
    return os.path.join(
        instance._meta.app_label,
        instance._meta.model_name,
        filename[:2],
        filename[2:4],
        filename,
    )


generic_upload_to = uuid_upload_to
