from django.urls import path

from . import views

app_name = 'images'
urlpatterns = [
    path('', views.index, name='index'),
    path('image/delete/<int:image_id>/', views.delete_images, name='delete_images'),
    path('image/setfree/<int:imageset_id>/', views.set_free, name='setfree_imageset'),
    path('image/upload/<int:imageset_id>/', views.upload_image, name='upload_image'),
    path('image/<int:image_id>/', views.view_image, name='view_image'),
    path('imagelist/<int:image_set_id>/', views.list_images, name='list_images'),
    path('imageset/<int:imageset_id>/label-upload/', views.label_upload, name='label_upload'),
    path('imageset/create/', views.create_imageset, name='create_imageset'),
    path('imageset/<int:imageset_id>/delete/', views.delete_imageset, name='delete_imageset'),
    path('imageset/<int:imageset_id>/pin/', views.toggle_pin_imageset, name='pin_imageset'),
    path('imageset/<int:imageset_id>/edit/', views.edit_imageset, name='edit_imageset'),
    path('imageset/<int:image_set_id>/', views.view_imageset, name='view_imageset'),
    path('imageset/<int:image_set_id>/download/', views.download_imageset_zip, name='download_imageset'),
    path('imageset/explore/', views.explore_imageset, name='explore_imageset'),
    path('imageset/imagetagger_dl_script.py', views.dl_script, name='dl_script'),
    path('api/imageset/load/', views.load_image_set, name='load_image_set'),
    path('api/imageset/tag/add/', views.tag_image_set, name='tag_image_set'),
    path('api/imageset/tag/delete/', views.remove_image_set_tag, name='remove_image_set_tag'),
    path('api/imageset/tag/autocomplete/', views.autocomplete_image_set_tag, name='autocomplete_image_set_tag'),
]
