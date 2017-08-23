from django.contrib.auth.models import Group
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Team(models.Model):
    name = models.CharField(
        verbose_name=_('team name'),
        validators=[MinLengthValidator(3), MaxLengthValidator(30)],
        max_length=100, unique=True)
    members = models.ForeignKey(Group,
                                related_name='members')
    admins = models.ForeignKey(Group,
                               related_name='admins')
    website = models.CharField(max_length=100, default='')

    def __str__(self):
        return u'Team: {0}'.format(self.name)

    class Meta:
        permissions = (
            ('user_management', 'Manage users'),
            ('create_set', 'Create imagesets'),
        )