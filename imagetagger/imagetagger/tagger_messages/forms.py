from django import forms

from imagetagger.tagger_messages.models import GlobalMessage, TeamMessage
from datetimewidget.widgets import DateTimeWidget

class TeamMessageCreationForm(forms.ModelForm):
    class Meta:
        model = TeamMessage
        fields = [
            'title',
            'content',
            'start_time',
            'expire_time',
            'admins_only',
            'team'
        ]

        widgets = {
            'start_time': DateTimeWidget(attrs={'id':"id_start_time"}, usel10n = True, bootstrap_version=3),
        }


class GlobalMessageCreationForm(forms.ModelForm):
    class Meta:
        model = GlobalMessage
        fields = [
            'title',
            'content',
            'start_time',
            'expire_time',
            'team_admins_only',
            'staff_only',
        ]
