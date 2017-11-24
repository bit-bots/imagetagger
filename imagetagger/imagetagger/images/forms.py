from django import forms

from imagetagger.images.models import ImageSet


class ImageSetCreationForm(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'public',
        ]


class ImageSetEditForm(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'description',
            'public',
            'image_lock',
        ]


class LabelUploadForm(forms.Form):
    class Meta:
        file = forms.FileField()
        verify = forms.CheckboxInput()
        verify.initial = False
