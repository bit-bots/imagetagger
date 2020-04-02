from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK

from imagetagger.annotations.models import Annotation, AnnotationType, ExportFormat, Export, Verification
from imagetagger.api import serializers
from imagetagger.api.permissions import ImageSetPermission, AnnotationPermission, VerificationPermission
from imagetagger.images.models import Image, ImageSet, SetTag
from imagetagger.users.models import Team, User, TeamMembership

TEAM_PERMISSIONS = ('create_set', 'user_management', 'manage_export_formats')
IMAGE_SET_PERMISSIONS = ('verify', 'annotate', 'create_export', 'delete_annotation', 'delete_export',
                         'delete_set', 'delete_images', 'edit_annotation', 'edit_set', 'read')


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = serializers.AnnotationSerializer
    permission_classes = (AnnotationPermission,)


class AnnotationTypeViewSet(viewsets.ModelViewSet):
    queryset = AnnotationType.objects.all()
    serializer_class = serializers.AnnotationTypeSerializer


class ExportFormatViewSet(viewsets.ModelViewSet):
    queryset = ExportFormat.objects.all()
    serializer_class = serializers.ExportFormatSerializer


class ExportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Export.objects.all()
    serializer_class = serializers.ExportSerializer


class ImageSetViewSet(viewsets.ModelViewSet):
    queryset = ImageSet.objects.prefetch_related('set_tags').select_related('team').annotate(number_of_images=Count('images'))
    permission_classes = (ImageSetPermission,)
    serializer_class = serializers.ImageSetSerializer

    @staticmethod
    def add_permissions(user, image_set, data):
        permission_set = image_set.get_perms(user)
        permission_dict = dict()
        for permission in IMAGE_SET_PERMISSIONS:
            permission_dict[permission] = permission in permission_set
        data['permissions'] = permission_dict
        return data

    def retrieve(self, request, *args, **kwargs):
        # TODO Move data enrichment into serializer or model
        image_set = self.get_object()
        serializer = self.get_serializer(image_set)
        data = self.add_permissions(request.user, image_set, serializer.data)
        data['isPinned'] = request.user in image_set.pinned_by.all()
        return Response(data)

    @action(methods=('PUT', 'DELETE'), detail=True)
    def pin(self, request, pk=None):
        image_set = get_object_or_404(ImageSet, pk=pk)
        user = request.user
        if 'read' in image_set.get_perms(request.user):
            if request.method == 'PUT' and user not in image_set.pinned_by.all():
                image_set.pinned_by.add(request.user)
                image_set.save()
                return Response(status=HTTP_201_CREATED)
            elif request.method == 'DELETE' and user in image_set.pinned_by.all():
                image_set.pinned_by.remove(request.user)
                image_set.save()
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_403_FORBIDDEN)


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = serializers.ImageSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = serializers.TeamSerializer

    @staticmethod
    def add_permissions(user, team, data):
        # TODO Move data enhancement into serializer
        permission_set = team.get_perms(user)
        permission_dict = dict()
        for permission in TEAM_PERMISSIONS:
            permission_dict[permission] = permission in permission_set
        data['permissions'] = permission_dict
        return data

    def retrieve(self, request, *args, **kwargs):
        team = self.get_object()
        serializer = self.get_serializer(team)
        data = self.add_permissions(request.user, team, serializer.data)
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        TeamMembership.objects.create(team=team, user=request.user, is_admin=True)
        return Response(serializer.data, status=HTTP_201_CREATED)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related('teams', 'pinned_sets')
    serializer_class = serializers.UserSerializer

    @action(('GET',), detail=False)
    def me(self, request):
        """
        Get information about the currently logged in user
        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    serializer_class = serializers.VerificationSerializer
    permission_classes = (VerificationPermission,)


class ImagesetTagViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    queryset = SetTag.objects.all()
    serializer_class = serializers.ImagesetTagSerializer
