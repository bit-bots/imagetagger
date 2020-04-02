from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from imagetagger.api import views

app_name = 'api'

router = DefaultRouter()
router.register(r'annotations', views.AnnotationViewSet, base_name='annotations')
router.register(r'annotation_types', views.AnnotationTypeViewSet, base_name='annotation_types')
router.register(r'export_formats', views.ExportFormatViewSet, base_name='export_formats')
router.register(r'exports', views.ExportViewSet, base_name='exports')
router.register(r'image_sets', views.ImageSetViewSet, base_name='image_sets')
router.register(r'images', views.ImageViewSet)
router.register(r'teams', views.TeamViewSet, base_name='teams')
router.register(r'users', views.UserViewSet, base_name='users')
router.register(r'verifications', views.VerificationViewSet, base_name='verifications')
router.register(r'image_set_tags', views.ImagesetTagViewSet, base_name='image_set_tags')

urlpatterns = [
    *router.urls,
    path('auth/', obtain_auth_token),
]
