from django import forms

from imagetagger.annotations.models import ExportFormat


class ExportFormatCreationForm(forms.ModelForm):
    class Meta:
        model = ExportFormat
        fields = [
            'name',
            'team',
            'annotations_types',
            'public',
            'base_format',
            'image_format',
            'annotation_format',
            'not_in_image_format',
            'min_verifications',
            'image_aggregation'
        ]