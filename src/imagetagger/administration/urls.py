from django.urls import path

from . import views

app_name = 'administration'
urlpatterns = [
    path('', views.annotation_types, name='index'),
    path('annotation_type/list/', views.annotation_types, name='annotation_types'),
    path('annotation_type/<int:annotation_type_id>/', views.annotation_type, name='annotation_type'),
    path('annotation_type/create/', views.create_annotation_type, name='create_annotation_type'),
    path('annotation_type/edit/<int:annotation_type_id>/', views.edit_annotation_type, name='edit_annotation_type'),
    path('annotation_type/migrate/bbt0p/<int:annotation_type_id>/', views.migrate_bounding_box_to_0_polygon, name='migrate_bbt0p'),
    path('annotation_type/migrate/bbt4p/<int:annotation_type_id>/', views.migrate_bounding_box_to_4_polygon, name='migrate_bbt4p'),
]
