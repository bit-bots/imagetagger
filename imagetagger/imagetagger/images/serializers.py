from rest_framework.serializers import ModelSerializer

from imagetagger.images.models import ImageSet, Image


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = (
            'id',
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

    def __init__(self, *args, **kwargs):
        images_annotation_type_filter = kwargs.get('images_annotation_type_filter')
        if images_annotation_type_filter:
            del kwargs['images_annotation_type_filter']
        super().__init__(*args, **kwargs)
        return
        if images_annotation_type_filter:
            print('foo')
            print(self.fields)
            print(self.fields['images'])
            self.fields['images'].queryset = self.fields['images'].queryset.exclude(
                annotations__annotation_type=images_annotation_type_filter)

    images = ImageSerializer(many=True)
