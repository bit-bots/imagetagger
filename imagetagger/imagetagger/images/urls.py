from django.conf.urls import url

from . import views

app_name = 'images'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^image/delete/(\d+)/$', views.delete_image, name='delete_image'),
    url(r'^image/setfree/(\d+)/$', views.set_free, name='setfree_imageset'),
    url(r'^image/upload/(\d+)/$', views.upload_image, name='upload_image'),
    url(r'^image/(\d+)/$', views.view_image, name='view_image'),
    url(r'^imagelist/(\d+)/$', views.list_images, name='list_images'),
    url(r'^imageset/(\d+)/label-upload/$', views.label_upload, name='label_upload'),
    url(r'^imageset/create/$', views.create_imageset, name='create_imageset'),
    url(r'^imageset/(\d+)/delete/$', views.delete_imageset, name='delete_imageset'),
    url(r'^imageset/(\d+)/pin/$', views.toggle_pin_imageset, name='pin_imageset'),
    url(r'^imageset/(\d+)/edit/$', views.edit_imageset, name='edit_imageset'),
    url(r'^imageset/(\d+)/$', views.view_imageset, name='view_imageset'),
    url(r'^imageset/explore/$', views.explore_imageset, name='explore_imageset'),
    url(r'^imageset/imagetagger_dl_script.py$', views.dl_script, name='dl_script'),
    url(r'^api/imageset/load/$', views.api_load_image_set, name='api_load_image_set'),
    url(r'^api/imageset/tag/add/$', views.api_tag_image_set, name='api_tag_image_set'),
    url(r'^api/imageset/tag/delete/$', views.api_remove_image_set_tag, name='api_remove_image_set_tag'),
    url(r'^api/imageset/tag/autocomplete/$', views.api_autocomplete_image_set_tag, name='api_autocomplete_image_set_tag'),
]
