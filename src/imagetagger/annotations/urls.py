from django.urls import path

from . import views

app_name = 'annotations'
urlpatterns = [
    path('export/create/', views.create_exportformat, name='create_exportformat'),
    path('export/<int:format_id>/edit/', views.edit_exportformat, name='edit_exportformat'),
    path('export/<int:format_id>/delete/', views.delete_exportformat, name='delete_exportformat'),
    path('export/<int:export_id>/auth/', views.export_auth, name='export_auth'),
    path('export/<int:export_id>/download/', views.download_export, name='download_export'),
    path('export/<int:image_set_id>/', views.create_export, name='create_export'),
    path('api/export/create/', views.api_create_export, name='api_create_export'),
    path('api/export_format/list/', views.api_get_export_formats, name='api_get_export_formats'),
    path('manage/annotation/<int:image_set_id>/', views.manage_annotations, name='manage_annotations'),
    path('manage/delete/<int:image_set_id>/', views.delete_annotations, name='delete_annotations'),
    path('<int:annotation_id>/delete/', views.delete_annotation, name='delete_annotation'),
    path('<int:image_id>/', views.annotate, name='annotate'),
    path('annotateset/<int:imageset_id>/', views.annotate_set, name='annotate_set'),
    path('<int:annotation_id>/verify/', views.verify, name='verify'),
    path('api/annotation/create/', views.create_annotation, name='create_annotation'),
    path('api/annotation/delete/', views.api_delete_annotation, name='delete_annotation'),
    path('api/annotation/load/', views.load_annotations, name='load_annotations'),  # loads annotations of an image
    path('api/annotation/loadset/', views.load_set_annotations, name='load_set_annotations'),  # loads annotations of an image
    path('api/annotation/loadannotationtypes/', views.load_annotation_types, name='load_annotation_types'),  # loads all active annotation types
    path('api/annotation/loadsetannotationtypes/', views.load_set_annotation_types, name='load_set_annotation_types'),  # loads annotations of an image
    path('api/annotation/loadfilteredset/', views.load_filtered_set_annotations, name='load_filtered_set_annotations'),  # loads filtered annotations of an image
    path('api/annotation/loadone/', views.load_annotation, name='load_annotation'),
    path('api/annotation/loadmultiple/', views.load_multiple_annotations, name='load_multiple_annotations'),
    path('api/annotation/verify/', views.api_verify_annotation, name='verify_annotation'),
    path('api/annotation/update/', views.update_annotation, name='update_annotations'),
    path('api/annotation/blurred_concealed/', views.api_blurred_concealed_annotation, name='blurred_concealed_annotation'),
]
