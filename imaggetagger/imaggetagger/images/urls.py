from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^overwiew/(\d+)/$', overview, name='images_overview'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^createset/$', image_set_creator, name='images_tagview'),
    ]