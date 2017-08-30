from rest_framework.serializers import ModelSerializer

from .models import Annotation, AnnotationType


class AnnotationTypeSerializer(ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = (
            'id',
            'name',
        )


class AnnotationSerializer(ModelSerializer):
    class Meta:
        model = Annotation
        fields = (
            'annotation_type',
            'content',
            'id',
            'vector',
        )

    annotation_type = AnnotationTypeSerializer(read_only=True)
