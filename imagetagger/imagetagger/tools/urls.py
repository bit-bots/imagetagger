from django.conf.urls import url

from . import views

app_name = 'tools'
urlpatterns = [
    url(r'^$', views.overview, name='overview'),
    url(r'^create/$', views.create_tool, name='create'),
    url(r'^delete/(\d+)/$', views.delete_tool, name='delete'),
    url(r'^edit/(\d+)/$', views.edit_tool, name='edit'),
    url(r'^download/(\d+)/$', views.download_tool, name='download'),
]
