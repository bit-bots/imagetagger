from django import forms

from imagetagger.annotations.models import AnnotationType


class AnnotationFormatCreationForm(forms.ModelForm):
    class Meta:
        model = AnnotationType
        fields = [
            'name',
            'active',
            'node_count',
            'vector_type',
        ]