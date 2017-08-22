from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group
import os

from imagetagger.users.models import Team


class Image(models.Model):
    image_set = models.ForeignKey('ImageSet', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    filename = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(auto_now_add=True)
    checksum = models.BinaryField()

    def path(self):
        return os.path.join(self.image_set.root_path(), self.filename)

    def relative_path(self):
        return os.path.join(self.image_set.path, self.filename)

    def __str__(self):
        return u'Image: {0}'.format(self.name)


class ImageSet(models.Model):
    path = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)
    time = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    public = models.BooleanField(default=False)
    image_lock = models.BooleanField(default=False)

    def root_path(self):
        return os.path.join(settings.IMAGE_PATH, self.path)

    def image_count(self):
        path = self.root_path()
        return len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

    def __str__(self):
        return u'Imageset: {0}'.format(self.name)

    class Meta:
        permissions = (
            ('edit_set', 'Edit set'),
            ('delete_set', 'Delete set'),
            ('edit_annotation', 'Edit annotations in the set'),
            ('delete_annotation', 'Delete annotations in the set'),
            ('annotate', 'Create annotations in the set'),
            ('read', 'Read and download annotations and images'),
            ('create_export', 'Create export files of the set'),
            ('delete_export', 'Delete export files of the set'),
        )
