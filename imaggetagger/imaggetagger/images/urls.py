from django.conf.urls import url
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import *

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^logout/', logout_view, name='images_logout'),
    url(r'^overwiew/(\d+)/$', overview, name='images_overview'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^tagview/(\d+)/edit/(\d+)/$', tageditview, name='images_tageditview'),
    url(r'^tagview/(\d+)/delete/(\d+)/$', tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/(\d+)/edit/(\d+)/save/$', tageditsaveview, name='images_tageditsaveview'),
    url(r'^export/(\d+)/$', exportview, name='images_exportview'),
    url(r'^export/(\d+)/create/$', exportcreateview, name='images_exportcreateview'),
    ]
