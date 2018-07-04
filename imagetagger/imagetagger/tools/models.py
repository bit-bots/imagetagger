from typing import Set

from imagetagger.users.models import Team
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Tool(models.Model):
    name = models.CharField(max_length=100)
    filename = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    team = models.ForeignKey(Team,
                             on_delete=models.SET_NULL,
                             related_name='tool_team',
                             null=True,
                             blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.SET_NULL,
                                related_name='tool_creator',
                                null=True,
                                blank=True)

    @property
    def internal_filename(self):
        return '{0}_{1}'.format(self.id, self.name)

    def get_perms(self, user: get_user_model()) -> Set[str]:
        """Get all permissions of the user."""
        perms = set()
        if self.creator is not None and self.creator.id is user.id:
            perms.update({
                'edit_tool',
                'delete_tool',
                'download_tool',
                'see_tool',
            })
        if self.team is not None:
            if self.team.is_admin(user):
                perms.update({
                    'edit_tool',
                    'delete_tool',
                    'download_tool',
                    'see_tool',
                })
            if self.team.is_member(user):
                perms.update({
                    'download_tool',
                    'see_tool',
                })
        if self.public:
            perms.update({
                'download_tool',
                'see_tool',
            })
        return perms

    def has_perm(self, permission: str, user: get_user_model()) -> bool:
        """Check whether user has a specified permission."""
        return permission in self.get_perms(user)


class ToolVote(models.Model):
    class Meta:
        unique_together = [
            'tool',
            'user',
        ]

    tool = models.ForeignKey(
        Tool, on_delete=models.CASCADE, related_name='tool')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    time = models.DateTimeField(auto_now_add=True)
    positive = models.BooleanField(default=0)
