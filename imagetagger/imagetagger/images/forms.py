from django import forms

from imagetagger.images.models import ImageSet


class ImageSetCreationForm(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'public',
            'public_collaboration',
        ]


class ImageSetEditForm(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'description',
            'public',
            'public_collaboration',
            'image_lock',
        ]


class LabelUploadForm(forms.Form):
    file = forms.FileField()
    verify = forms.BooleanField(required=None)
