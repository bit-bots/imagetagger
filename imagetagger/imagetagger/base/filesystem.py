import fs
import fs.base
from django.conf import settings


def root() -> fs.base.FS:
    """Get the root filesystem object or create one by opening `settings.FS_URL`."""
    if root._instance is None:
        root._instance = fs.open_fs(settings.FS_URL)
    return root._instance

root._instance = None


def tmp() -> fs.base.FS:
    """Get the tmp filesystem object or create one by opening `settings.TMP_FS_URL`."""
    if tmp._instance is None:
        tmp._instance = fs.open_fs(settings.TMP_FS_URL)
    return tmp._instance

tmp._instance = None