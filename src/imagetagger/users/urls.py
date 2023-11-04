from django.urls import path

from . import views


app_name = 'users'
urlpatterns = [
    path('api/user/autocomplete/', views.user_autocomplete, name='user_autocomplete'),
    path('team/<int:team_id>/', views.view_team, name='team'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/explore/', views.explore_team, name='explore_team'),
    path('team/<int:team_id>/add/', views.add_team_member, name='add_team_member'),
    path('team/<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('team/<int:team_id>/leave/<int:user_id>/', views.leave_team, name='leave_team'),
    path('team/<int:team_id>/grant_admin/<int:user_id>/', views.grant_team_admin, name='grant_team_admin'),
    path('team/<int:team_id>/revoke_admin/<int:user_id>/', views.revoke_team_admin, name='revoke_team_admin'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/<int:user_id>/delete/', views.delete_account, name='delete_account'),
    path('user/explore/', views.explore_user, name='explore_user'),
]
