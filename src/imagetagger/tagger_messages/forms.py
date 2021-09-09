from django import forms

from imagetagger.tagger_messages.models import GlobalMessage, TeamMessage


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
