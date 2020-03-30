from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from imagetagger.api.views import ImageViewSet, AnnotationViewSet, AnnotationTypeViewSet, ExportFormatViewSet, \
    ExportViewSet, ImageSetViewSet, TeamViewSet, UserViewSet, VerificationViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'annotations', AnnotationViewSet, base_name='annotations')
router.register(r'annotation_types', AnnotationTypeViewSet, base_name='annotation_types')
router.register(r'export_formats', ExportFormatViewSet, base_name='export_formats')
router.register(r'exports', ExportViewSet, base_name='exports')
router.register(r'image_sets', ImageSetViewSet, base_name='image_sets')
router.register(r'images', ImageViewSet)
router.register(r'teams', TeamViewSet, base_name='teams')
router.register(r'users', UserViewSet, base_name='users')
router.register(r'verifications', VerificationViewSet, base_name='verifications')

urlpatterns = [
    *router.urls,
    path('auth/', obtain_auth_token),
]
