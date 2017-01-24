from django.conf.urls import url
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import index, logout_view, overview, tagview, tageditview, tagdeleteview, tageditsaveview, exportcreateview, export_auth_view, exportdownloadview

urlpatterns = [
    url(r'^$', index, name='images_index'),
    url(r'^export/(\d+)/auth/$', export_auth_view, name='images_export_auth'),
    url(r'^logout/', logout_view, name='images_logout'),
    url(r'^overview/(\d+)/$', overview, name='images_overview'),
    url(r'^tagview/(\d+)/$', tagview, name='images_tagview'),
    url(r'^tagview/(\d+)/edit/(\d+)/$', tageditview, name='images_tageditview'),
    url(r'^tagview/(\d+)/delete/(\d+)/$', tagdeleteview, name='images_tagdeleteview'),
    url(r'^tagview/(\d+)/edit/(\d+)/save/$', tageditsaveview, name='images_tageditsaveview'),
    url(r'^export/(\d+)/$', exportcreateview, name='images_exportview'),
    url(r'^export/(\d+)/download/$', exportdownloadview, name='images_exportdownloadview'),
    # url(r'^export/(\d+)/create/$', exportcreateview, name='images_exportcreateview'),
]
