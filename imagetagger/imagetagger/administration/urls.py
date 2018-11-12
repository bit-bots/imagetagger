from django.conf.urls import url

from . import views

app_name = 'administration'
urlpatterns = [
    url(r'^$', views.annotation_types, name='index'),
    url(r'^annotation_type/list/$', views.annotation_types, name='annotation_types'),
    url(r'^annotation_type/(\d+)/$', views.annotation_type, name='annotation_type'),
    url(r'^annotation_type/create/$', views.create_annotation_type, name='create_annotation_type'),
    url(r'^annotation_type/create_view/$', views.create_annotation_type_view, name='create_annotation_type_view'),
    url(r'^annotation_type/edit/(\d+)/$', views.edit_annotation_type, name='edit_annotation_type'),
    url(r'^annotation_type/migrate/bbt0p/(\d+)/$', views.migrate_bounding_box_to_0_polygon, name='migrate_bbt0p'),
    url(r'^annotation_type/migrate/bbt4p/(\d+)/$', views.migrate_bounding_box_to_4_polygon, name='migrate_bbt4p'),
]
