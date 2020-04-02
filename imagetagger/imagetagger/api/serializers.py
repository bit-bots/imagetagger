from django.urls import reverse
from rest_framework import serializers

from imagetagger.annotations.models import Annotation, AnnotationType, ExportFormat, Export, Verification
from imagetagger.images.models import Image, ImageSet, SetTag
from imagetagger.users.models import Team, User


class CurrentUserAsListDefault(serializers.CurrentUserDefault):
    def __call__(self):
        current_user = super().__call__()
        return [current_user]


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ('id', 'concealed', 'blurred', 'last_edit_time', 'not_in_image',
                  'vector', 'image', 'annotation_type', 'creator', 'last_editor')

    creator = serializers.HiddenField(source='user', default=serializers.CurrentUserDefault())
    concealed = serializers.BooleanField(source='_concealed')
    blurred = serializers.BooleanField(source='_blurred')
    not_in_image = serializers.SerializerMethodField()

    @staticmethod
    def get_not_in_image(instance):
        return instance.vector is None


class AnnotationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = ('id', 'name', 'active', 'vector_type', 'node_count',
                  'enable_concealed', 'enable_blurred')


class ExportFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportFormat
        fields = ('id', 'name', 'last_change_time', 'public', 'base_format', 'image_format',
                  'annotation_format', 'vector_format', 'not_in_image_format', 'name_format',
                  'min_verifications', 'image_aggregation', 'include_blurred', 'include_concealed')


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = ('id', 'time', 'annotation_count', 'url', 'deprecated',
                  'format', 'image_set', 'creator')

    creator = serializers.PrimaryKeyRelatedField(source="user", read_only=True)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'name', 'width', 'height', 'url', 'annotations')

    url = serializers.SerializerMethodField()
    annotations = serializers.PrimaryKeyRelatedField(many=True, queryset=Annotation.objects.all())

    @staticmethod
    def get_url(instance: Image):
        route_name = "images:view_image"
        return reverse(route_name, args=(instance.id,))


class ImageSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSet
        fields = ('id', 'name', 'location', 'description', 'time', 'public',
                  'public_collaboration', 'image_lock', 'priority', 'zip_state',
                  'images', 'main_annotation_type', 'tags', 'team', 'creator',
                  'zip_url', 'number_of_images')

    tags = serializers.ListField(source="tag_names", child=serializers.CharField(), allow_empty=True, default=[])
    creator = serializers.PrimaryKeyRelatedField(
        default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault()),
        queryset=User.objects.all())    # TODO Make read_only which breaks setting a default
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    zip_url = serializers.SerializerMethodField()
    number_of_images = serializers.IntegerField(source="image_count", read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    @staticmethod
    def get_zip_url(instance: ImageSet):
        route_name = "images:download_imageset"
        return reverse(route_name, args=(instance.id,))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'points', 'pinned_sets', 'teams')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'members', 'website')

    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(),
                                                 default=serializers.CreateOnlyDefault(CurrentUserAsListDefault()))


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ('id', 'time', 'verification_value', 'creator', 'annotation')

    creator = serializers.PrimaryKeyRelatedField(source="user", read_only=True)
    verification_value = serializers.BooleanField(source="verified")


class ImagesetTagSerializer(serializers.BaseSerializer):
    def to_representation(self, instance: SetTag):
        return instance.name