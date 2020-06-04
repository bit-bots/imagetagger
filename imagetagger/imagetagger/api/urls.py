from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from imagetagger.api import views

app_name = 'api'

router = DefaultRouter()
router.register(r'annotations', views.AnnotationViewSet, basename='annotations')
router.register(r'annotation_types', views.AnnotationTypeViewSet, basename='annotation_types')
router.register(r'export_formats', views.ExportFormatViewSet, basename='export_formats')
router.register(r'exports', views.ExportViewSet, basename='exports')
router.register(r'image_sets', views.ImageSetViewSet, basename='image_sets')
router.register(r'images', views.ImageViewSet)
router.register(r'teams', views.TeamViewSet, basename='teams')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'verifications', views.VerificationViewSet, basename='verifications')
router.register(r'image_set_tags', views.ImagesetTagViewSet, basename='image_set_tags')

urlpatterns = [
    *router.urls,
    path('auth/', obtain_auth_token),
]
