from rest_framework.serializers import ModelSerializer

from imagetagger.images.models import ImageSet, Image, SetTag


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = (
            'id',
            'name',
        )


class SetTagSerializer(ModelSerializer):
    class Meta:
        model = SetTag
        fields = (
            'name',
        )


class ImageSetSerializer(ModelSerializer):
    class Meta:
        model = ImageSet
        fields = (
            'id',
            'name',
            'location',
            'description',
            'images',
        )

    images = ImageSerializer(many=True)
