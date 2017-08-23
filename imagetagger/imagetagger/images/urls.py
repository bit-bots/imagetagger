from django.conf.urls import url

from . import views

app_name = 'images'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^image/delete/(\d+)/$', views.delete_images, name='delete_images'),
    url(r'^image/(\d+)/$', views.view_image, name='view_image'),
    url(r'^imagelist/(\d+)/$', views.list_images, name='list_images'),
    # this view will be shadowed by nginx via image_nginx auth and direct access
    url(r'^image_nginx/(\d+)/$', views.view_image, name='view_image'),
    url(r'^imageset/(\d+)/create/$', views.create_imageset, name='create_imageset'),
    url(r'^imageset/(\d+)/delete/$', views.delete_imageset, name='delete_imageset'),
    url(r'^imageset/(\d+)/edit/$', views.edit_imageset, name='edit_imageset'),
    url(r'^imageset/(\d+)/$', views.view_imageset, name='view_imageset'),
    url(r'^imageset/explore/$', views.explore_imageset, name='explore_imageset'),
    url(r'^imageset/imagetagger_dl_script.sh$', views.dl_script, name='dl_script'),
    url(r'^image/upload/(\d+)/$', views.upload_image, name='upload_image'),
]
