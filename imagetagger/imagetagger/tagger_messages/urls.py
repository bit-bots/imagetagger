from django.conf.urls import url

from . import views

app_name = 'tagger_messages'
urlpatterns = [
    url(r'^tagger_messages/send_message/team_message/$', views.send_team_message, name='send_team_message'),
    url(r'^tagger_messages/send_message/global_message/$', views.send_global_message, name='send_global_message'),
]
