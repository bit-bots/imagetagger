from django.conf.urls import url

from . import views


app_name = 'users'
urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^team/(\d+)/$', views.view_team, name='team'),
    url(r'^team/create/$', views.create_team, name='create_team'),
    url(r'^team/explore/$', views.explore_team, name='explore_team'),
    url(r'^team/(\d+)/leave/$', views.leave_team, name='leave_team'),
    url(r'^team/(\d+)/leave/(\d+)/$', views.leave_team, name='kick_user'),
    url(r'^team/(\d+)/enthrone/(\d+)/$', views.enthrone, name='enthrone_user'),
    url(r'^team/(\d+)/dethrone/(\d+)/$', views.dethrone, name='dethrone_user'),
    url(r'^user/(\d+)/$', views.user, name='user'),
    url(r'^user/explore/$', views.explore_user, name='explore_user'),
]
