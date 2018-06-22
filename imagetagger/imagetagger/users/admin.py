from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Team, TeamMembership, User

admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(User, UserAdmin)
