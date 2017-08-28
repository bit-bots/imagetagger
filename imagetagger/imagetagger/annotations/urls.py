from django.conf.urls import url

from . import views

app_name = 'annotations'
urlpatterns = [
    url(r'^export/(\d+)/auth/$', views.export_auth, name='export_auth'),
    url(r'^export/(\d+)/download/$', views.download_export, name='download_export'),
    url(r'^export/(\d+)/$', views.create_export, name='create_export'),
    url(r'^manage/annotation/(\d+)/$', views.manage_annotations, name='manage_annotations'),
    url(r'^(\d+)/delete/$', views.delete_annotation, name='delete_annotation'),
    url(r'^(\d+)/$', views.annotate, name='annotate'),
    url(r'^(\d+)/edit/save/$', views.edit_annotation_save, name='edit_annotation_save'),
    url(r'^(\d+)/edit/$', views.edit_annotation, name='edit_annotation'),
    url(r'^(\d+)/verify/$', views.verify, name='verify'),
    url(r'^api/annotation/create/$', views.create_annotation, name='create_annotation'),
    url(r'^api/annotation/delete/$', views.api_delete_annotation, name='delete_annotation'),
    url(r'^api/annotation/load/$', views.load_annotations, name='load_annotations'),
]
