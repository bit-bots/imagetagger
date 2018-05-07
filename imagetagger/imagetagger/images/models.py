from typing import Set

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import Group
import os

from imagetagger.users.models import Team


class Image(models.Model):
    image_set = models.ForeignKey(
        'ImageSet', on_delete=models.CASCADE, related_name='images')
    name = models.CharField(max_length=100)
    filename = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(auto_now_add=True)
    checksum = models.BinaryField()
    width = models.IntegerField(default=800)
    height = models.IntegerField(default=600)

    def path(self):
        return os.path.join(self.image_set.root_path(), self.filename)

    def relative_path(self):
        return os.path.join(self.image_set.path, self.filename)

    def __str__(self):
        return u'Image: {0}'.format(self.name)


class ImageSet(models.Model):
    class Meta:
        unique_together = [
            'name',
            'team',
        ]
    PRIORITIES = (
        (1, 'High'),
        (0, 'Normal'),
        (-1, 'Low'),
    )

    path = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)
    time = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name='image_sets',
        null=True,
        blank=True
    )
    public = models.BooleanField(default=False)
    public_collaboration = models.BooleanField(default=False)
    image_lock = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITIES, default=0)
    main_annotation_type = models.ForeignKey(
        to='annotations.AnnotationType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    def root_path(self):
        return os.path.join(settings.IMAGE_PATH, self.path)

    def image_count(self):
        path = self.root_path()
        return len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

    def get_perms(self, user: get_user_model()) -> Set[str]:
        """Get all permissions of the user."""
        perms = set()
        if self.team is not None:
            if self.team.is_admin(user):
                perms.update({
                    'verify',
                    'annotate',
                    'create_export',
                    'delete_annotation',
                    'delete_export',
                    'delete_set',
                    'edit_annotation',
                    'edit_set',
                    'read',
                })
            if self.team.is_member(user):
                perms.update({
                    'verify',
                    'annotate',
                    'create_export',
                    'delete_annotation',
                    'delete_export',
                    'edit_annotation',
                    'edit_set',
                    'read',
                })
        if self.public:
            perms.update({
                'read',
                'create_export',
            })
            if self.public_collaboration:
                perms.update({
                    'verify',
                    'annotate',
                    'delete_annotation',
                    'edit_annotation',
                })
        return perms

    def has_perm(self, permission: str, user: get_user_model()) -> bool:
        """Check whether user has specified permission."""
        return permission in self.get_perms(user)

    def __str__(self):
        return u'Imageset: {0}'.format(self.name)

    @property
    def prio_symbol(self):
        if self.priority is -1:
            return '<span class="glyphicon glyphicon-download" data-toggle="tooltip" data-placement="right" title="Low labeling priority"></span>'
        elif self.priority is 0:
            return ''
        elif self.priority is 1:
            return '<span class="glyphicon glyphicon-exclamation-sign" data-toggle="tooltip" data-placement="right" title="High labeling priority"></span>'
