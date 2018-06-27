from django.conf import settings
from imagetagger.users.models import Team


def base_data(request):
    if request.user.is_authenticated:
        my_teams = Team.objects.filter(members=request.user)
    else:
        my_teams = None

    return {
        'IMPRINT_URL': settings.IMPRINT_URL,
        'USE_IMPRINT': settings.USE_IMPRINT,
        'IMPRINT_NAME': settings.IMPRINT_NAME,
        'TOOLS_ENABLED': settings.TOOLS_ENABLED,
        'my_teams': my_teams,
    }

