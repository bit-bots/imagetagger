from typing import List
from os.path import join, dirname
from django.core.checks import register, CheckMessage, Error
from django.conf import settings
from fs.base import FS
from . import filesystem


def _create_check_file(fs: FS, path: str):
    fs.makedirs(dirname(path), recreate=True)
    fs.create(path, wipe=True)
    fs.writebytes(path, bytes('This is a demo file content', encoding='ASCII'))
    fs.remove(path)


@register
def check_fs_root_config(app_configs, **kwargs) -> List[CheckMessage]:
    try:
        _create_check_file(filesystem.root(), join(settings.IMAGE_PATH, 'check.tmp.jpeg'))
        _create_check_file(filesystem.root(), join(settings.TOOLS_PATH, 'check.tmp.py'))
        return []
    except Exception as e:
        return [Error(
            'Persistent filesystem is incorrectly configured. Could not create and delete a temporary check file',
            hint=f'Check your FS_URL settings (currently {settings.FS_URL})',
            obj=e,
        )]


@register
def check_tmp_fs_config(app_configs, **kwargs) -> List[CheckMessage]:
    try:
        _create_check_file(filesystem.tmp(), join(settings.TMP_IMAGE_PATH, 'check.tmp.jpeg'))
        return []
    except Exception as e:
        return [Error(
            'Persistent filesystem is incorrectly configured. Could not create and delete a temporary check file',
            hint=f'Check your TMP_FS_URL settings (currently {settings.TMP_FS_URL})',
            obj=e,
        )]
