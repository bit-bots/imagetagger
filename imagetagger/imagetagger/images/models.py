
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group
import os
# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ForeignKey(Group,
                                related_name='members')
    admins = models.ForeignKey(Group,
                               related_name='admins')
    website = models.CharField(max_length=100)

    def __str__(self):
        return u'Team: {0}'.format(self.name)

    class Meta:
        permissions = (
            ('user_management', 'Manage users'),
            ('create_set', 'Create imagesets'),
        )


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


class Image(models.Model):
    image_set = models.ForeignKey(ImageSet, on_delete=models.CASCADE)
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


class AnnotationType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return u'AnnotationType: {0}'.format(self.name)


class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    vector = models.CharField(max_length=1000)
    closed = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(AnnotationType, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='creator',
                             on_delete=models.SET_NULL,
                             null=True)
    last_edit_time = models.DateTimeField(null=True, blank=True)
    last_editor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='last_editor',
                                    null=True,
                                    on_delete=models.SET_NULL)
    verified_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Verification')
    not_in_image = models.BooleanField(default=0)  # if True, the object is definitely not in the image

    def __str__(self):
        return u'Annotation: {0}'.format(self.type.name)

    def content(self):
        if self.not_in_image:
            return 'Not in image'
        else:
            return self.vector

    def verification_count(self):
        return (Verification.objects.filter(annotation=self.id).filter(verified=True).count() - Verification.objects.filter(annotation=self.id).filter(verified=False).count())

    def owner(self):
        return self.last_editor if self.last_editor else self.user


class Verification(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=0)


class Export(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    image_set = models.ForeignKey(ImageSet)
    type = models.CharField(max_length=50)
    annotation_count = models.IntegerField(default=0)
    export_text = models.TextField(default='')

    def __str__(self):
        return u'Export: {0}'.format(self.id)

