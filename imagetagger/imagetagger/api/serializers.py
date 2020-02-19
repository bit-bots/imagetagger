from django.urls import reverse
from dynamic_rest import serializers as serializers
from dynamic_rest import fields

from imagetagger.annotations.models import Annotation, AnnotationType, ExportFormat, Export, Verification
from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team, User


class NotInImageField(fields.DynamicComputedField):
    def get_attribute(self, instance):
        return instance.vector is None


class ReverseRouteField(fields.DynamicComputedField):
    def __init__(self, route_name, instance_field_name, requires=None, deferred=None, field_type=None, immutable=False, **kwargs):
        super().__init__(requires, deferred, field_type, immutable, **kwargs)
        self.route_name = route_name
        self.instance_field_name = instance_field_name

    def get_attribute(self, instance):
        instance_field = getattr(instance, self.instance_field_name)
        return reverse(self.route_name, args=(instance_field,))


class AnnotationSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = Annotation
        fields = ('id', 'concealed', 'blurred', 'last_edit_time', 'user', 'not_in_image',
                  'vector', 'image', 'annotation_type', 'creator', 'last_editor')

    creator = serializers.DynamicRelationField("UserSerializer", source="user", read_only=True)
    concealed = fields.DynamicField(source="_concealed")
    blurred = fields.DynamicField(source="_blurred")
    not_in_image = NotInImageField()

    user = fields.fields.HiddenField(default=serializers.serializers.CurrentUserDefault())

    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # concealed = serializers.BooleanField(source='_concealed')
    # blurred = serializers.BooleanField(source='_blurred')
    # not_in_image = serializers.SerializerMethodField(read_only=True)


class AnnotationTypeSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = AnnotationType
        fields = ('id', 'name', 'active', 'vector_type', 'node_count',
                  'enable_concealed', 'enable_blurred')


class ExportFormatSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = ExportFormat
        fields = ('id', 'name', 'last_change_time', 'public', 'base_format', 'image_format',
                  'annotation_format', 'vector_format', 'not_in_image_format', 'name_format',
                  'min_verifications', 'image_aggregation', 'include_blurred', 'include_concealed')


class ExportSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = Export
        fields = ('id', 'time', 'annotation_count', 'url', 'deprecated',
                  'format', 'image_set', 'creator')

    creator = serializers.DynamicRelationField("UserSerializer", source="user", read_only=True)


class ImageSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'name', 'width', 'height', 'url', 'annotations')

    url = ReverseRouteField("images:view_image", "id")
    annotations = fields.DynamicRelationField("AnnotationSerializer", many=True)


class ImageSetSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = ImageSet
        fields = ('id', 'name', 'location', 'description', 'time', 'public',
                  'public_collaboration', 'image_lock', 'priority', 'zip_state',
                  'images', 'main_annotation_type', 'tags', 'team', 'creator',
                  'zip_url', 'number_of_images')

    tags = fields.DynamicField(source="tag_names")
    creator = serializers.DynamicRelationField("UserSerializer", read_only=True)
    team = serializers.DynamicRelationField("TeamSerializer", read_only=True)
    zip_url = ReverseRouteField("images:download_imageset", "id")
    number_of_images = fields.DynamicField(source="image_count")
    images = fields.DynamicRelationField("ImageSerializer", many=True)


class UserSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'points', 'pinned_sets', 'teams')


class TeamSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'members', 'website')

    members = fields.DynamicRelationField("UserSerializer", many=True, sideloading=False)


class VerificationSerializer(serializers.DynamicModelSerializer):
    class Meta:
        model = Verification
        fields = ('id', 'time', 'verification_value', 'creator', 'annotation')

    creator = fields.DynamicRelationField("UserSerializer", source="user", read_only=True)
    verification_value = fields.DynamicField(source="verified")

    # verification_value = serializers.BooleanField(source='verified')
    # creator = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
