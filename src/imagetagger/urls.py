"""imagetagger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.shortcuts import render
from django_registration.backends.activation.views import RegistrationView

from .users.forms import UserRegistrationForm

urlpatterns = [
    path('user/', include('django.contrib.auth.urls')),
    path('accounts/register/', RegistrationView.as_view(form_class=UserRegistrationForm), name='django_registration_register'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('', include('imagetagger.base.urls')),
    path('admin/', admin.site.urls),
    path('administration/', include('imagetagger.administration.urls')),
    path('annotations/', include('imagetagger.annotations.urls')),
    path('images/', include('imagetagger.images.urls')),
    path('users/', include('imagetagger.users.urls')),
    path('tagger_messages/', include('imagetagger.tagger_messages.urls')),
    path('tools/', include('imagetagger.tools.urls')),
]


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    use_sentry = False
    sentry_dsn = None
    event_id = None
    try:
        import sentry_sdk
        if sentry_sdk.Hub.current.client:
            use_sentry = True
            sentry_dsn = sentry_sdk.Hub.current.client.dsn
            event_id = sentry_sdk.last_event_id()
    except ImportError:
        pass

    return render(request, '500.html', status=500, context={
        'use_sentry': use_sentry,
        'sentry_dsn': sentry_dsn,
        'event_id': event_id,
    })
