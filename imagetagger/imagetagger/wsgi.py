"""
WSGI config for imagetagger project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from configurations.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imagetagger.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Prod")

application = get_wsgi_application()
