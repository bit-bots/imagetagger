from django.conf.urls import url

from . import views

app_name = 'images'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^image/delete/(\d+)/$', views.delete_images, name='delete_images'),
    url(r'^image/setfree/(\d+)/$', views.set_free, name = 'setfree_imageset'),
    url(r'^image/upload/(\d+)/$', views.upload_image, name='upload_image'),
    url(r'^image/(\d+)/$', views.view_image, name='view_image'),
    url(r'^imagelist/(\d+)/$', views.list_images, name='list_images'),
    url(r'^imageset/(\d+)/label-upload/$', views.label_upload, name='label_upload'),
    url(r'^imageset/create/$', views.create_imageset, name='create_imageset'),
    url(r'^imageset/(\d+)/delete/$', views.delete_imageset, name='delete_imageset'),
    url(r'^imageset/(\d+)/edit/$', views.edit_imageset, name='edit_imageset'),
    url(r'^imageset/(\d+)/$', views.view_imageset, name='view_imageset'),
    url(r'^imageset/explore/$', views.explore_imageset, name='explore_imageset'),
    url(r'^imageset/imagetagger_dl_script.py$', views.dl_script, name='dl_script'),
    url(r'^api/imageset/load/$', views.load_image_set, name='load_image_set'),
    url(r'^api/imageset/tag/add/$', views.tag_image_set, name='tag_image_set'),
    url(r'^api/imageset/tag/delete/$', views.remove_image_set_tag, name='remove_image_set_tag'),
    url(r'^api/imageset/tag/autocomplete/$', views.autocomplete_image_set_tag, name='autocomplete_image_set_tag'),
]
