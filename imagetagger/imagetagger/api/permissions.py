from rest_framework.permissions import BasePermission

from imagetagger.annotations.models import Annotation
from imagetagger.images.models import Image
from imagetagger.users.models import TeamMembership


class ImageTaggerPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return self.has_create_permission(request)
        else:
            # List is always allowed, the others depend on has_object_permission
            return True

    def has_object_permission(self, request, view, obj):
        if view.action == 'destroy':
            return self.has_destroy_permission(request, obj)
        elif view.action == 'update':
            return self.has_update_permission(request, obj)
        else:
            # Retrieve is always okay
            return True

    def has_create_permission(self, request):
        return True

    def has_destroy_permission(self, request, obj):
        return True

    def has_update_permission(self, request, obj):
        return True


class ImageSetPermission(ImageTaggerPermission):
    def has_create_permission(self, request):
        if 'team' not in request.data:
            return False
        else:
            return TeamMembership.objects.filter(team_id=request.data['team'], user=request.user).exists()

    def has_update_permission(self, request, obj):
        return (request.user == obj.creator or
                TeamMembership.objects.filter(team=obj.team, user=request.user).exists())

    def has_destroy_permission(self, request, obj):
        return TeamMembership.objects.filter(team=obj.team, user=request.user, is_admin=True).exists()


class AnnotationPermission(ImageTaggerPermission):
    def has_create_permission(self, request):
        if 'image' not in request.data:
            return False
        else:
            image = Image.objects.get(id=request.data['image'])
            return (image.image_set.public_collaboration or
                    image.image_set.creator == request.user or
                    TeamMembership.objects.filter(team=image.image_set.team, user=request.user))

    def has_update_permission(self, request, obj):
        return (obj.image_set.public_collaboration or
                obj.image_set.creator == request.user or
                TeamMembership.objects.filter(team=obj.image_set.team, user=request.user))

    def has_destroy_permission(self, request, obj):
        return (obj.image.image_set.public_collaboration or
                obj.image.image_set.creator == request.user or
                TeamMembership.objects.filter(team=obj.image.image_set.team, user=request.user))


class VerificationPermission(ImageTaggerPermission):
    def has_create_permission(self, request):
        if 'annotation' not in request.data:
            return False
        else:
            annotation = Annotation.objects.select_related('image__image_set').get(id=request.data['annotation'])
            return (annotation.image.image_set.public_collaboration or
                    annotation.image.image_set.creator == request.user or
                    TeamMembership.objects.filter(team=annotation.image.image_set.team, user=request.user))

    def has_destroy_permission(self, request, obj):
        return False

    def has_update_permission(self, request, obj):
        return obj.creator == request.user

