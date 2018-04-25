from django.conf.urls import url

from . import views

app_name = 'administration'
urlpatterns = [
    url(r'^$', views.annotation_types, name='index'),
    url(r'^annotation_type/list/$', views.annotation_types, name='annotation_types'),
    url(r'^annotation_type/(\d+)/$', views.annotation_type, name='annotation_type'),
    url(r'^annotation_type/create/$', views.create_annotation_type, name='create_annotation_type'),
]
