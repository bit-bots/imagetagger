from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^overwiew/(\d+)/$', overview, name='images_overview'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^tagview/(\d+)/edit/(\d+)/$', tageditview, name='images_tageditview'),
    url(r'^tagview/(\d+)/delete/(\d+)/$', tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/(\d+)/edit/(\d+)/save/$', tageditsaveview, name='images_tageditsaveview'),
    ]
