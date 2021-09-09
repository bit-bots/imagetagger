from django import forms

from imagetagger.tools.models import Tool
from django.core.exceptions import ValidationError


# found this under:
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')


class ToolUploadForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = [
            'team',
            'name',
            'description',
            'public',
        ]
    file = forms.FileField(max_length=250, required=True, validators=[file_size])


class FileUploadForm(forms.Form):
    file = forms.FileField(max_length=250, required=False, validators=[file_size])
