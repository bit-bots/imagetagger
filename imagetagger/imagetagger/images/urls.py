from django.conf.urls import url
from django.contrib import auth

from . import views

urlpatterns = [
    url(r'^$', views.index, name='images_index'),
    url(r'^export/(\d+)/auth/$', views.export_auth_view, name='images_export_auth'),
    url(r'^logout/', views.logout_view, name='images_logout'),
    url(r'^imageset/(\d+)/$', views.imagesetview, name='images_imagesetview'),
    url(r'^imageset/create/(\d+)/$', views.imagesetcreateview, name='images_imagesetcreateview'),
    url(r'^imageset/edit/(\d+)/$', views.imageseteditview, name='images_imageseteditview'),
    url(r'^imageset/delete/(\d+)/$', views.imagesetdeleteview, name='images_imagesetdeleteview'),
    url(r'^imageset/explore/$', views.exploreview, {'mode': 'imageset'}, name='images_exploreimagesetview'),
    url(r'^imageset/imagetagger_dl_script.sh$', views.dl_script, name='images_dl_script'),
    url(r'^tagview/(\d+)/$', views.tagview, name='images_tagview'),
    url(r'^tagview/edit/(\d+)/$', views.tageditview, name='images_tageditview'),
    url(r'^tagview/delete/(\d+)/$', views.tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/edit/(\d+)/save/$', views.tageditsaveview, name='images_tageditsaveview'),
    url(r'^export/(\d+)/$', views.exportcreateview, name='images_exportview'),
    url(r'^export/(\d+)/download/$', views.exportdownloadview, name='images_exportdownloadview'),
    url(r'^manage/annotation/(\d+)/$', views.annotationmanageview, name='images_annotationmanageview'),
    url(r'^verify/(\d+)/$', views.verifyview, name='images_verifyview'),
    url(r'^imagelist/(\d+)/$', views.get_image_list, name='images_imagelist'),
    url(r'^image/(\d+)/$', views.imageview, name='images_imageview'),
    # this view will be shadowed by nginx via image_nginx auth and direct access
    url(r'^image_nginx/(\d+)/$', views.imageview, name='images_nginx_imageauth'),
    url(r'^image/upload/(\d+)/$', views.imageuploadview, name='images_imageuploadview'),
    url(r'^image/delete/(\d+)/$', views.imagedeleteview, name='images_imagedeleteview'),
    url(r'^user/(\d+)/$', views.userview, name='images_userview'),
    url(r'^user/create/$', views.createuserview, name='images_createuserview'),
    url(r'^user/explore/$', views.exploreview, {'mode': 'user'}, name='images_exploreuserview'),
    url(r'^team/(\d+)/$', views.teamview, name='images_teamview'),
    url(r'^team/create/$', views.createteamview, name='images_createteamview'),
    url(r'^team/explore/$', views.exploreview, {'mode': 'team'}, name='images_exploreteamview'),
    url(r'^team/(\d+)/leave/$', views.leaveteamview, name='images_leaveteamview'),
    url(r'^team/(\d+)/leave/(\d+)/$', views.leaveteamview, name='images_kickuserview'),
    url(r'^team/(\d+)/enthrone/(\d+)/$', views.enthroneview, name='images_enthroneuserview'),
    url(r'^team/(\d+)/dethrone/(\d+)/$', views.dethroneview, name='images_dethroneuserview'),
]
