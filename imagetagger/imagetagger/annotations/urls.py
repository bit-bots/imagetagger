from django.conf.urls import url

from . import views

app_name = 'annotations'
urlpatterns = [
    url(r'^export/(\d+)/create/$', views.create_exportformat, name='create_exportformat'),
    url(r'^export/(\d+)/edit/$', views.edit_exportformat, name='edit_exportformat'),
    url(r'^export/(\d+)/delete/$', views.delete_exportformat, name='delete_exportformat'),
    url(r'^export/(\d+)/auth/$', views.export_auth, name='export_auth'),
    url(r'^export/(\d+)/download/$', views.download_export, name='download_export'),
    url(r'^export/(\d+)/$', views.create_export, name='create_export'),
    url(r'^manage/annotation/(\d+)/$', views.manage_annotations, name='manage_annotations'),
    url(r'^(\d+)/delete/$', views.delete_annotation, name='delete_annotation'),
    url(r'^(\d+)/$', views.annotate, name='annotate'),
    url(r'^(\d+)/verify/$', views.verify, name='verify'),
    url(r'^api/annotation/create/$', views.create_annotation, name='create_annotation'),
    url(r'^api/annotation/delete/$', views.api_delete_annotation, name='delete_annotation'),
    url(r'^api/annotation/load/$', views.load_annotations, name='load_annotations'),  # loads annotations of an image
    url(r'^api/annotation/loadset/$', views.load_set_annotations, name='load_set_annotations'),  # loads annotations of an image
    url(r'^api/annotation/loadannotationtypes/$', views.load_annotation_types, name='load_annotation_types'),  # loads all active annotation types
    url(r'^api/annotation/loadsetannotationtypes/$', views.load_set_annotation_types, name='load_set_annotation_types'),  # loads annotations of an image
    url(r'^api/annotation/loadfilteredset/$', views.load_filtered_set_annotations, name='load_filtered_set_annotations'),  # loads filtered annotations of an image
    url(r'^api/annotation/loadone/$', views.load_annotation, name='load_annotation'),
    url(r'^api/annotation/verify/$', views.api_verify_annotation, name='verify_annotation'),
    url(r'^api/annotation/update/$', views.update_annotation, name='update_annotations'),
]
