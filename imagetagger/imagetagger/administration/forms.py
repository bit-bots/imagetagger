from django import forms

from imagetagger.annotations.models import AnnotationType


class AnnotationTypeCreationForm(forms.ModelForm):
    class Meta:
        model = AnnotationType
        fields = [
            'name',
            'active',
            'node_count',
            'vector_type',
            'enable_concealed',
            'enable_blurred',
            'md_description',
        ]


class AnnotationTypeEditForm(forms.ModelForm):
    class Meta:
        model = AnnotationType
        fields = [
            'name',
            'active',
            'enable_concealed',
            'enable_blurred',
            'md_description',
        ]
