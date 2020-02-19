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
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django_registration.backends.activation.views import RegistrationView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .users.forms import UserRegistrationForm

schema_view = get_schema_view(
    openapi.Info(
        title="Imagetagger Api",
        default_version="v1",
        contact=openapi.Contact("Bit-Bots <info@bit-bots.de>"),
        license=openapi.License("MIT", "https://github.com/bit-bots/imagetagger/blob/master/LICENSE")
    ),
    public=True,
)

urlpatterns = [
    url(r'^user/', include('django.contrib.auth.urls')),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegistrationForm), name='django_registration_register'),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^', include('imagetagger.base.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^administration/', include('imagetagger.administration.urls')),
    url(r'^annotations/', include('imagetagger.annotations.urls')),
    url(r'^images/', include('imagetagger.images.urls')),
    url(r'^users/', include('imagetagger.users.urls')),
    url(r'^tagger_messages/', include('imagetagger.tagger_messages.urls')),
    url(r'^tools/', include('imagetagger.tools.urls')),
    url(r'^api/', include('imagetagger.api.urls')),
    url(r'^schema.json$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
    url(r'^docs/$', schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui")
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    return render(request, '500.html', status=500)
