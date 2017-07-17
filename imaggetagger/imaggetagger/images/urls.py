from django.conf.urls import url
from django.contrib import auth
from .views import *

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^export/(\d+)/auth/$', export_auth_view, name='images_export_auth'),
    url(r'^logout/', logout_view, name='images_logout'),
    url(r'^imageset/(\d+)/$', imagesetview, name='images_imagesetview'),
    url(r'^imageset/create/(\d+)/$', imagesetcreateview, name='images_imagesetcreateview'),
    url(r'^imageset/edit/(\d+)/$', imageseteditview, name='images_imageseteditview'),
    url(r'^imageset/delete/(\d+)/$', imagesetdeleteview, name='images_imagesetdeleteview'),
    url(r'^imageset/explore/$', exploreview, {'mode': 'imageset'}, name='images_exploreimagesetview'),
    url(r'^imageset/imagetagger_dl_script.sh$', dl_script, name='images_dl_script'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^tagview/edit/(\d+)/$', tageditview, name='images_tageditview'),
    url(r'^tagview/delete/(\d+)/$', tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/edit/(\d+)/save/$', tageditsaveview, name='images_tageditsaveview'),
    url(r'^export/(\d+)/$', exportcreateview, name='images_exportview'),
    url(r'^export/(\d+)/download/$', exportdownloadview, name='images_exportdownloadview'),
    url(r'^manage/annotation/(\d+)/$', annotationmanageview, name='images_annotationmanageview'),
    url(r'^verify/(\d+)/$', verifyview, name='images_verifyview'),
    url(r'^imagelist/(\d+)/$', get_image_list, name='images_imagelist'),
    # this view will be shadowed by nginx via image_nginx auth and direct access
    url(r'^image/(\d+)/$', imageview, name='images_imageview'),
    url(r'^image_nginx/(\d+)/$', image_auth_nginx, name='images_nginx_imageauth'),
    url(r'^image/upload/(\d+)/$', imageuploadview, name='images_imageuploadview'),
    url(r'^image/delete/(\d+)/$', imagedeleteview, name='images_imagedeleteview'),
    url(r'^user/(\d+)/$', userview, name='images_userview'),
    url(r'^user/create/$', createuserview, name='images_createuserview'),
    url(r'^user/explore/$', exploreview, {'mode': 'user'}, name='images_exploreuserview'),
    url(r'^team/(\d+)/$', teamview, name='images_teamview'),
    url(r'^team/create/$', createteamview, name='images_createteamview'),
    url(r'^team/explore/$', exploreview, {'mode': 'team'}, name='images_exploreteamview'),
    url(r'^team/(\d+)/leave/$', leaveteamview, name='images_leaveteamview'),
    url(r'^team/(\d+)/leave/(\d+)/$', leaveteamview, name='images_kickuserview'),
    url(r'^team/(\d+)/enthrone/(\d+)/$', enthroneview, name='images_enthroneuserview'),
    url(r'^team/(\d+)/dethrone/(\d+)/$', dethroneview, name='images_dethroneuserview'),
]
