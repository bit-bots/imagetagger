from django.contrib.auth.models import Group
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ForeignKey(Group,
                                related_name='members')
    admins = models.ForeignKey(Group,
                               related_name='admins')
    website = models.CharField(max_length=100)

    def __str__(self):
        return u'Team: {0}'.format(self.name)

    class Meta:
        permissions = (
            ('user_management', 'Manage users'),
            ('create_set', 'Create imagesets'),
        )