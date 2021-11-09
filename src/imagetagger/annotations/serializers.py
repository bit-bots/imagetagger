from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

from .models import Annotation, AnnotationType, Verification, ExportFormat
from imagetagger.images.serializers import ImageSerializer


class AnnotationTypeSerializer(ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = (
            'id',
            'name',
            'vector_type',
            'node_count',
            'enable_concealed',
            'enable_blurred',
        )


class AnnotationListSerializer(ModelSerializer):
    class Meta:
        model = Annotation
        fields = (
            'id',
            'annotation_type',
            'vector',
            'image',
        )

    image = ImageSerializer(read_only=True)


class AnnotationSerializer(ModelSerializer):
    verified_by_user = SerializerMethodField('is_verified_by_user')

    def is_verified_by_user(self, annotation):

        user = self.context['request'].user
        return Verification.objects.filter(user=user, annotation=annotation).exists()

    class Meta:
        model = Annotation
        fields = (
            'annotation_type',
            'id',
            'vector',
            'verified_by_user',
            'image',
            'concealed',
            'blurred',
        )

    annotation_type = AnnotationTypeSerializer(read_only=True)
    image = ImageSerializer(read_only=True)


class ExportFormatInfoSerializer(ModelSerializer):
    team_name = CharField(source='team.name')

    class Meta:
        model = ExportFormat
        fields = (
            'name',
            'id',
            'team_name',
        )
