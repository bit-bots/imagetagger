
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return u'Annotation: {0}'.format(self.type.name)
