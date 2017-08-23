from django import forms
from django.contrib.auth.models import User

from .models import Team


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
