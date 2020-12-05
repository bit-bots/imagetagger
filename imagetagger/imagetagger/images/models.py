from typing import Set

from fs import path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

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
        return path.combine(self.image_set.root_path(), self.filename)

    def relative_path(self):
        return path.combine(self.image_set.path, self.filename)

    def delete(self, *args, **kwargs):
        self.image_set.zip_state = ImageSet.ZipState.INVALID
        self.image_set.save(update_fields=('zip_state',))
        super(Image, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.image_set.zip_state = ImageSet.ZipState.INVALID
        self.image_set.save(update_fields=('zip_state',))
        super(Image, self).save(*args, **kwargs)

    def __str__(self):
        return u'Image: {0}'.format(self.name)


class ImageSet(models.Model):
    class Meta:
        unique_together = [
            'name',
            'team',
        ]

    class ZipState:
        INVALID = 0
        READY = 1
        PROCESSING = 2

    PRIORITIES = (
        (1, 'High'),
        (0, 'Normal'),
        (-1, 'Low'),
    )
    ZIP_STATES = (
        (ZipState.INVALID, 'invalid'),
        (ZipState.READY, 'ready'),
        (ZipState.PROCESSING, 'processing'),
    )

    path = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name='image_sets',
        null=True,
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                default=None,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
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
    pinned_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='pinned_sets')
    zip_state = models.IntegerField(choices=ZIP_STATES, default=ZipState.INVALID)

    def root_path(self):
        return path.combine(settings.IMAGE_PATH, self.path)

    def tmp_path(self):
        return path.combine(settings.TMP_IMAGE_PATH, self.path)

    def relative_zip_path(self):
        return path.combine(self.path, self.zip_name())

    def zip_path(self):
        return path.combine(self.root_path(), self.zip_name())

    def tmp_zip_path(self):
        return path.combine(self.tmp_path(), self.zip_name())

    def zip_name(self):
        return "imageset_{}.zip".format(self.id)

    @property
    def image_count(self):
        if hasattr(self, 'image_count_agg'):
            return self.image_count_agg
        return self.images.count()

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
                    'delete_images',
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
            if user == self.creator:
                perms.update({
                    'verify',
                    'annotate',
                    'create_export',
                    'delete_annotation',
                    'delete_export',
                    'delete_set',
                    'delete_images',
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
        if self.priority == -1:
            return '<span class="glyphicon glyphicon-download" data-toggle="tooltip" data-placement="right" title="Low labeling priority"></span>'
        elif self.priority == 0:
            return ''
        elif self.priority == 1:
            return '<span class="glyphicon glyphicon-exclamation-sign" data-toggle="tooltip" data-placement="right" title="High labeling priority"></span>'


class SetTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    imagesets = models.ManyToManyField(ImageSet, related_name='set_tags')
