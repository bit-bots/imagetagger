from django import forms

from imagetagger.images.models import ImageSet


class ImageMetadataForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    image = forms.HiddenInput()


class ImageSetCreationForm(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'public',
            'public_collaboration',
        ]


class ImageSetCreationFormWT(forms.ModelForm):
    class Meta:
        model = ImageSet
        fields = [
            'name',
            'location',
            'public',
            'public_collaboration',
            'team',
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
            'priority',
            'main_annotation_type',
        ]


class LabelUploadForm(forms.Form):
    file = forms.FileField()
    verify = forms.BooleanField(required=None)
