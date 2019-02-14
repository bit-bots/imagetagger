from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from imagetagger.annotations.models import Annotation, AnnotationType, ExportFormat, Export, Verification
from imagetagger.api.serializers import ImageSerializer, AnnotationSerializer, AnnotationTypeSerializer, \
    ExportFormatSerializer, ExportSerializer, ImageSetSerializer, TeamSerializer, UserSerializer, VerificationSerializer
from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team, User


TEAM_PERMISSIONS = ('create_set', 'user_management', 'manage_export_formats')
IMAGE_SET_PERMISSIONS = ('verify', 'annotate', 'create_export', 'delete_annotation', 'delete_export',
                         'delete_set', 'delete_images', 'edit_annotation', 'edit_set', 'read')


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
    queryset = ImageSet.objects.prefetch_related('set_tags')
    serializer_class = ImageSetSerializer

    @staticmethod
    def add_permissions(user, image_set, data):
        permissions = dict()
        for permission in IMAGE_SET_PERMISSIONS:
            permissions[permission] = image_set.has_perm(permission, user)
        data['permissions'] = permissions
        return data

    def retrieve(self, request, pk=None):
        image_set = get_object_or_404(ImageSet, pk=pk)
        serializer = ImageSetSerializer(image_set)
        data = self.add_permissions(request.user, image_set, serializer.data)
        return Response(data)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @staticmethod
    def add_permissions(user, team, data):
        permissions = dict()
        for permission in TEAM_PERMISSIONS:
            permissions[permission] = team.has_perm(permission, user)
        data['permissions'] = permissions
        return data

    def retrieve(self, request, pk=None):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team)
        data = self.add_permissions(request.user, team, serializer.data)
        return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('teams', 'pinned_sets')
    serializer_class = UserSerializer

    @action(('GET',), detail=False)
    def me(self, request):
        """
        Get information about the currently logged in user
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
