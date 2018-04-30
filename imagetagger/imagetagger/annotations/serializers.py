from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Annotation, AnnotationType, Verification


class AnnotationTypeSerializer(ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = (
            'id',
            'name',
            'vector_type',
            'node_count',
        )


class AnnotationSerializer(ModelSerializer):
    verified_by_user = SerializerMethodField('is_verified_by_user')

    def is_verified_by_user(self, annotation):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return Verification.objects.filter(user=user, annotation=annotation).exists()
        return False

    class Meta:
        model = Annotation
        fields = (
            'annotation_type',
            'content',
            'id',
            'vector',
            'verified_by_user',
        )

    annotation_type = AnnotationTypeSerializer(read_only=True)
