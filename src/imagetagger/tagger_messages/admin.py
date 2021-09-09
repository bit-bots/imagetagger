from django.contrib import admin

from .models import TeamMessage, GlobalMessage

admin.site.register(TeamMessage)
admin.site.register(GlobalMessage)
