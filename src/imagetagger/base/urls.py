from django.conf.urls import url

from . import views

app_name = 'base'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^problems/$', views.problem_report, name='problem')
]
