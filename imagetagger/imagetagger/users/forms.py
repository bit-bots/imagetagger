from django import forms
from registration.forms import RegistrationForm

from .models import Team, User


class UserRegistrationForm(RegistrationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name',
        ]
