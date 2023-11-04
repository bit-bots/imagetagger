from django.urls import path

from . import views

app_name = 'base'
urlpatterns = [
    path('', views.index, name='index'),
    path('problems/', views.problem_report, name='problem')
]
