from django.contrib import admin

from .models import Team, TeamMembership

admin.site.register(Team)
admin.site.register(TeamMembership)
