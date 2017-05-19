from django.conf.urls import url
from django.contrib import auth
from .views import index, logout_view, overview, tagview, tageditview, tagdeleteview, tageditsaveview, exportcreateview, export_auth_view, exportdownloadview, annotationmanageview, verifyview, userview, groupview, creategroupview, createuserview

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^export/(\d+)/auth/$', export_auth_view, name='images_export_auth'),
    url(r'^logout/', logout_view, name='images_logout'),
    url(r'^overview/(\d+)/$', overview, name='images_overview'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^tagview/edit/(\d+)/$', tageditview, name='images_tageditview'),
    url(r'^tagview/delete/(\d+)/$', tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/edit/(\d+)/save/$', tageditsaveview, name='images_tageditsaveview'),
    url(r'^export/(\d+)/$', exportcreateview, name='images_exportview'),
    url(r'^export/(\d+)/download/$', exportdownloadview, name='images_exportdownloadview'),
    url(r'^manage/annotation/(\d+)/$', annotationmanageview, name='images_annotationmanageview'),
    url(r'^verify/(\d+)/$', verifyview, name='images_verifyview'),
    url(r'^user/(\d+)/$', userview, name='images_userview'),
    url(r'^user/create/$', createuserview, name='images_createuserview'),
    url(r'^group/(\d+)/$', groupview, name='images_groupview'),
    url(r'^group/create/$', creategroupview, name='images_creategroupview'),
    # url(r'^export/(\d+)/create/$', exportcreateview, name='images_exportcreateview'),
]
