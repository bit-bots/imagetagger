from django.db import models
from imagetagger.users.models import Team
from django.conf import settings


class Tool(models.Model):
    name = models.CharField(max_length=100)
    filename = models.CharField(max_length=255)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
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

