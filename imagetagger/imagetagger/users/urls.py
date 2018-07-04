from django.conf.urls import url

from . import views


app_name = 'users'
urlpatterns = [
    url(r'^api/user/autocomplete/$', views.user_autocomplete, name='user_autocomplete'),
    url(r'^team/(\d+)/$', views.view_team, name='team'),
    url(r'^team/create/$', views.create_team, name='create_team'),
    url(r'^team/explore/$', views.explore_team, name='explore_team'),
    url(r'^team/(\d+)/add/$', views.add_team_member, name='add_team_member'),
    url(r'^team/(\d+)/leave/$', views.leave_team, name='leave_team'),
    url(r'^team/(\d+)/leave/(\d+)/$', views.leave_team, name='leave_team'),
    url(r'^team/(\d+)/grant_admin/(\d+)/$', views.grant_team_admin, name='grant_team_admin'),
    url(r'^team/(\d+)/revoke_admin/(\d+)/$', views.revoke_team_admin, name='revoke_team_admin'),
    url(r'^user/(\d+)/$', views.user, name='user'),
    url(r'^user/explore/$', views.explore_user, name='explore_user'),
]
