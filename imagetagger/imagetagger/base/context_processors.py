from django.conf import settings


def base_data(request):
    return {
        'IMPRINT_URL': settings.IMPRINT_URL,
        'USE_IMPRINT': settings.USE_IMPRINT,
        'IMPRINT_NAME': settings.IMPRINT_NAME,
        'TOOLS_ENABLED': settings.TOOLS_ENABLED,
    }

