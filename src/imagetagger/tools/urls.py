from django.urls import path

from . import views

app_name = 'tools'
urlpatterns = [
    path('', views.overview, name='overview'),
    path('create/', views.create_tool, name='create'),
    path('delete/<int:tool_id>/', views.delete_tool, name='delete'),
    path('edit/<int:tool_id>/', views.edit_tool, name='edit'),
    path('download/<int:tool_id>/', views.download_tool, name='download'),
]
