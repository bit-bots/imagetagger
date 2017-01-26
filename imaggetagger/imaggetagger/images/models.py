
from django.conf import settings
from django.db import models

# Create your models here.


class ImageSet(models.Model):
    path = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)

    def get_path(self):
        return str(settings.IMAGE_PATH + self.path + '/')

    def __str__(self):
        return u'Imageset: {0}'.format(self.name)


class Image(models.Model):
    image_set = models.ForeignKey(ImageSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    # LOCATION

    def full_path(self):
        return str(self.image_set.get_path() + self.name)

    def __str__(self):
        return u'Image: {0}'.format(self.name)


class AnnotationType(models.Model):
    name = models.CharField(max_length=50)

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
                                    null=True)

    def __str__(self):
        return u'Annotation: {0}'.format(self.type.name)


class Export(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    image_set = models.ForeignKey(ImageSet)
    type = models.CharField(max_length=50)
    annotation_count = models.IntegerField(default=0)
    export_text = models.TextField(default='')

    def __str__(self):
        return u'Export: {0}'.format(self.id)
