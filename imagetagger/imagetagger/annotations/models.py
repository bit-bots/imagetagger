from django.conf import settings
from django.db import models
from django.db.models import Subquery, F, IntegerField, OuterRef
from django.utils.functional import cached_property

from imagetagger.images.models import Image, ImageSet


class AnnotationQuerySet(models.QuerySet):
    def annotate_verification_difference(self) -> models.QuerySet:
        return self.annotate(
            positive_verifications_count=Subquery(
                Verification.objects.filter(
                    annotation_id=OuterRef('pk'), verified=False).values(
                    'annotation_id').annotate(
                    count=F('pk')).values('count'),
                output_field=IntegerField()),
            negative_verifications_count=Subquery(
                Verification.objects.filter(
                    annotation_id=OuterRef('pk'), verified=True).values(
                    'annotation_id').annotate(
                    count=F('pk')).values('count'),
                output_field=IntegerField())).annotate(
            verification_difference=F(
                'positive_verifications_count') - F('negative_verifications_count'))


class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    vector = models.CharField(max_length=1000)
    closed = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('AnnotationType', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='creator',
                             on_delete=models.SET_NULL,
                             null=True)
    last_edit_time = models.DateTimeField(null=True, blank=True)
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='last_editor', null=True,
        on_delete=models.SET_NULL)
    verified_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Verification')
    not_in_image = models.BooleanField(default=0)  # if True, the object is definitely not in the image

    objects = models.Manager.from_queryset(AnnotationQuerySet)()

    def __str__(self):
        return 'Annotation: {0}'.format(self.type.name)

    def content(self):
        if self.not_in_image:
            return 'Not in image'
        else:
            return self.vector

    def owner(self):
        return self.last_editor if self.last_editor else self.user


class AnnotationType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return u'AnnotationType: {0}'.format(self.name)


class Export(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    image_set = models.ForeignKey(ImageSet)
    type = models.CharField(max_length=50)
    annotation_count = models.IntegerField(default=0)
    export_text = models.TextField(default='')

    def __str__(self):
        return u'Export: {0}'.format(self.id)


class Verification(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=0)
