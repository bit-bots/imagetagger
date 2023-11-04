from django.urls import path

from . import views

app_name = 'tagger_messages'
urlpatterns = [
    path('send_message/team_message/', views.send_team_message, name='send_team_message'),
    path('send_message/global_message/', views.send_global_message, name='send_global_message'),
    path('read_message/<int:message_id>/', views.read_message, name='read_message'),
    path('read_message/all/', views.read_all_messages, name='read_all_messages'),
    path('read_message/global_message/all/', views.read_all_annoucements, name='read_all_annoucements'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('overview/', views.overview_unread, name='overview'),
    path('overview/unread/', views.overview_unread, name='overview_unread'),
    path('overview/all/', views.overview_all, name='overview_all'),
    path('overview/sent/', views.overview_sent_active, name='overview_sent'),
    path('overview/sent/active/', views.overview_sent_active, name='overview_sent_active'),
    path('overview/sent/hidden/', views.overview_sent_hidden, name='overview_sent_hidden'),
    path('overview/global/', views.overview_global_active, name='overview_global'),
    path('overview/global/active/', views.overview_global_active, name='overview_global_active'),
    path('overview/global/hidden/', views.overview_global_hidden, name='overview_global_hidden'),
]
