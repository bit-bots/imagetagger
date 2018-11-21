import fasteners
import os
from time import sleep

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Q
from zipfile import ZipFile

from imagetagger.images.models import ImageSet


class Command(BaseCommand):
    help = 'Runs a daemon that creates zip archives for image sets and keeps them up to date'

    def handle(self, *args, **options):
        if not settings.ENABLE_ZIP_DOWNLOAD:
            raise CommandError('To enable zip download, set ENABLE_ZIP_DOWNLOAD to True in settings.py')

        lock = fasteners.InterProcessLock(os.path.join(settings.IMAGE_PATH, 'zip.lock'))
        gotten = lock.acquire(blocking=False)
        if gotten:
            while True:
                for imageset in ImageSet.objects.filter(~Q(zip_state=ImageSet.ZipState.READY)):
                    self._regenerate_zip(imageset)
                sleep(10)
        else:
            raise CommandError('The lockfile is present. There seems to be another instance of the zip daemon running.\n'
                               'Please stop it before starting a new one.\n'
                               'If this problem persists, delete {}.\n'.format(lock.path))

    def _regenerate_zip(self, imageset):
        updated = ImageSet.objects.filter(pk=imageset.pk) \
            .filter(~Q(zip_state=ImageSet.ZipState.READY)) \
            .update(zip_state=ImageSet.ZipState.PROCESSING)
        if not updated:
            self.stderr.write('skipping regeneration of ready imageset {}'.format(imageset.name))
            return

        with ZipFile(os.path.join(settings.IMAGE_PATH, imageset.tmp_zip_path()), 'w') as f:
            for image in imageset.images.all():
                f.write(image.path(), image.name)

        os.rename(os.path.join(settings.IMAGE_PATH, imageset.tmp_zip_path()),
                  os.path.join(settings.IMAGE_PATH, imageset.zip_path()))

        # Set state to ready if image set has not been set to invalid during regeneration
        ImageSet.objects.filter(pk=imageset.pk, zip_state=ImageSet.ZipState.PROCESSING) \
            .update(zip_state=ImageSet.ZipState.READY)
