import json
from enum import Enum
from typing import Set, Dict, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models, connection
from django.db.models import Subquery, F, IntegerField, OuterRef, QuerySet, Count
from django.db.models.functions import Coalesce

from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team


class AnnotationQuerySet(models.QuerySet):
    def annotate_verification_difference(self) -> models.QuerySet:
        return self.annotate(
            positive_verifications_count=Coalesce(Subquery(
                Verification.objects.filter(
                    annotation_id=OuterRef('pk'), verified=True).values(
                    'annotation_id').annotate(
                    count=Count('pk')).values('count'),
                output_field=IntegerField()), 0),
            negative_verifications_count=Coalesce(Subquery(
                Verification.objects.filter(
                    annotation_id=OuterRef('pk'), verified=False).values(
                    'annotation_id').annotate(
                    count=Count('pk')).values('count'),
                output_field=IntegerField()), 0)).annotate(
            verification_difference=F(
                'positive_verifications_count') - F('negative_verifications_count'))


class Annotation(models.Model):
    class VECTOR_TYPE(Enum):
        # TODO: VECTOR_TYPE could be deduced from the annotation type (dynamically, bonus points!)
        BOUNDING_BOX = 1

    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='annotations')
    vector = JSONField(null=True)
    closed = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

    annotation_type = models.ForeignKey('AnnotationType', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='creator',
                             on_delete=models.SET_NULL,
                             null=True)
    last_edit_time = models.DateTimeField(null=True, blank=True)
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='last_editor', null=True,
        on_delete=models.SET_NULL)
    verified_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Verification')

    objects = models.Manager.from_queryset(AnnotationQuerySet)()

    def __str__(self):
        return 'Annotation: {0}'.format(self.annotation_type.name)

    @property
    def height(self):
        return self.vector['y2']-self.vector['y1']

    @property
    def width(self):
        return self.vector['x2']-self.vector['x1']

    @property
    def radius(self):
        return (self.height + self.width)/2

    @property
    def diameter(self):
        return self.radius*2

    @property
    def center(self):
        xc = self.vector['y1'] + (self.height/2)
        yc = self.vector['x1'] + (self.width/2)
        return {'xc': xc, 'yc': yc }

    @property
    def relative_vector(self):
        x1rel = self.vector['x1']/self.image.width
        x2rel = self.vector['x2']/self.image.width
        y1rel = self.vector['y1']/self.image.height
        y2rel = self.vector['y2']/self.image.height
        return {'x1': x1rel, 'x2': x2rel, 'y1': y1rel, 'y2': y2rel}

    @property
    def relative_center(self):
        xc_rel = self.center['xc']/self.image.width
        yc_rel = self.center['yc']/self.image.height
        return {'xc': xc_rel, 'yc': yc_rel}

    @property
    def relative_width(self):
        rel_width = self.width/self.image.width
        return rel_width

    @property
    def relative_height(self):
        rel_height = self.height/self.image.height
        return rel_height

    @property
    def relative_radius(self):
        rel_rad_w = self.radius/self.image.width
        rel_rad_h = self.radius/self.image.height
        return (rel_rad_h + rel_rad_w)/2

    @property
    def relative_diameter(self):
        return self.relative_radius*2

    @property
    def not_in_image(self) -> bool:
        """Check whether the annotated object is not in the image."""
        return not self.vector

    @property
    def content(self):
        if self.not_in_image:
            return 'Not in image'
        return self.vector

    @property
    def vector_as_json(self) -> str:
        return json.dumps(self.vector)

    def owner(self):
        # TODO: maybe use an owner field populated by a database trigger
        return self.last_editor if self.last_editor else self.user

    def verify(self, user: get_user_model(), verified: bool):
        """Add or update a verification for an annotation."""
        if not self.verifications.filter(user=user).update(verified=verified):
            Verification.objects.create(
                annotation=self, user=user, verified=verified)

    @staticmethod
    def similar_annotations(
            vector: Union[dict, None], image: Image,
            annotation_type: 'AnnotationType', max_similarity: int = 5,
            exclude: Union[None, Set[int]] = None) -> bool:
        """
        Test for duplicates of same tag type and similiar coordinates
        (+-5 on every coordinate) on image.

        :param max_similarity specifies the maximum pixels each coordinate
            can differ to be regarded as similar.
        :param exclude a set of ids to exclude from checking
        """
        # TODO: Support dynamic VECTOR_TYPEs
        # TODO: Support returning explicit query sets instead of bool

        if vector is None:
            annotations = image.annotations.all()
            if exclude is not None:
                annotations = annotations.exclude(pk__in=exclude)
            return annotations.filter(
                annotation_type=annotation_type, vector__isnull=True).exists()

        query = '''
        SELECT
            (1)
        FROM
          {Annotation} a
        WHERE
          a.annotation_type_id=%(annotation_type_id)s AND
          a.image_id=%(image_id)s AND
          (vector->>'x1')::INT BETWEEN %(min_x1)s AND %(max_x1)s AND
          (vector->>'x2')::INT BETWEEN %(min_x2)s AND %(max_x2)s AND
          (vector->>'y1')::INT BETWEEN %(min_y1)s AND %(max_y1)s AND
          (vector->>'y2')::INT BETWEEN %(min_y2)s AND %(max_y2)s
        '''
        query_params = {
                'annotation_type_id': annotation_type.pk,
                'image_id': image.pk,
                'min_x1': vector.get('x1', 0) - max_similarity,
                'max_x1': vector.get('x1', 0) + max_similarity,
                'min_x2': vector.get('x2', 0) - max_similarity,
                'max_x2': vector.get('x2', 0) + max_similarity,
                'min_y1': vector.get('y1', 0) - max_similarity,
                'max_y1': vector.get('y1', 0) + max_similarity,
                'min_y2': vector.get('y2', 0) - max_similarity,
                'max_y2': vector.get('y2', 0) + max_similarity,
            }
        if exclude:
            query += ' AND a.id NOT IN %(exclude)s'
            query_params['exclude'] = tuple(exclude)

        with connection.cursor() as cursor:
            cursor.execute(query.format(**{
                'Annotation': Annotation._meta.db_table,
            }), query_params)
            return cursor.fetchone() is not None

    @staticmethod
    def validate_vector(vector: Union[dict, None],
                        vector_type: 'Annotation.VECTOR_TYPE') -> bool:
        """
        Validate a vector. Returns whether the vector is valid.
        Necessary type casts are done in-place within the dictionary.
        """
        if vector is None:
            # not in image
            return True
        if not isinstance(vector, dict):
            return False
        for key, value in vector.items():
            try:
                vector[key] = int(value)
            except ValueError:
                return False
        if vector_type == Annotation.VECTOR_TYPE.BOUNDING_BOX:
            return Annotation._validate_bounding_box(vector)

        # No valid vector type given.
        return False

    @staticmethod
    def _validate_bounding_box(vector: dict) -> bool:
        return (
            vector.get('x2', float('-inf')) -
            vector.get('x1', float('inf')) >= 1) and (
            vector.get('y2', float('-inf')) -
            vector.get('y1', float('inf')) >= 1
        )


class AnnotationType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return u'AnnotationType: {0}'.format(self.name)


class Export(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    image_set = models.ForeignKey(ImageSet,
                                  on_delete=models.CASCADE)
    annotation_count = models.IntegerField(default=0)
    export_text = models.TextField(default='')
    filename = models.TextField(default='')
    format = models.ForeignKey('ExportFormat',
                               on_delete=models.PROTECT,
                               related_name='exports')

    def __str__(self):
        return u'Export: {0}({1})'.format(self.id, self.filename)


class Verification(models.Model):
    class Meta:
        unique_together = [
            'annotation',
            'user',
        ]

    annotation = models.ForeignKey(
        Annotation, on_delete=models.CASCADE, related_name='verifications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True)
    time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=0)


class ExportFormat(models.Model):
    name = models.CharField(max_length=20, unique=True)
    annotations_types = models.ManyToManyField(AnnotationType)
    team = models.ForeignKey(Team, on_delete=models.PROTECT,
                             related_name='export_formats')
    public = models.BooleanField(default=False)
    base_format = models.TextField()  #more general, has a placeholder for the list of annotation_formats, can contain header, footer etc.
    image_format = models.TextField(null=True, blank=True, default=None)
    annotation_format = models.TextField() #used for every annotation in export (coordinates, type, image)
    name_format = models.CharField(default='export_%%exportid.txt', max_length=200)
    not_in_image_format = models.TextField()
    min_verifications = models.IntegerField(default=0)
    image_aggregation = models.BooleanField(default=False)

    def __str__(self):
        return '{}: {}'.format(self.team.name, self.name)
