import os


def uuid_upload_to(instance, filename):
    """
    Expects a uuid as the filename.
    """
    return os.path.join(
        filename[:2],
        filename[2:4],
        filename,
    )
