from django import forms

from .models import Team, User


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
        ]


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name',
        ]
