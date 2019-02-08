from rest_framework import viewsets

from imagetagger.annotations.models import Annotation, AnnotationType, ExportFormat, Export, Verification
from imagetagger.api.serializers import ImageSerializer, AnnotationSerializer, AnnotationTypeSerializer, \
    ExportFormatSerializer, ExportSerializer, ImageSetSerializer, TeamSerializer, UserSerializer, VerificationSerializer
from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team, User


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


class AnnotationTypeViewSet(viewsets.ModelViewSet):
    queryset = AnnotationType.objects.all()
    serializer_class = AnnotationTypeSerializer


class ExportFormatViewSet(viewsets.ModelViewSet):
    queryset = ExportFormat.objects.all()
    serializer_class = ExportFormatSerializer


class ExportViewSet(viewsets.ModelViewSet):
    queryset = Export.objects.all()
    serializer_class = ExportSerializer


class ImageSetViewSet(viewsets.ModelViewSet):
    queryset = ImageSet.objects.all()
    serializer_class = ImageSetSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('teams', 'pinned_sets')
    serializer_class = UserSerializer


class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
