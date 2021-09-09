from django.contrib.auth import get_user_model
from django.test import TestCase

from imagetagger.images.models import ImageSet
from imagetagger.users.models import Team, TeamMembership


class ImageTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='foo', email='foo@bar.baz', password='foobar123')
        self.team = Team.objects.create(name='aa')
        self.image_set = ImageSet.objects.create(name='foo', location='foo', team=self.team)

    def test_permissions_nonpublic_nonmember(self):
        """Test if the permissions are correct."""
        self.assertEquals(self.image_set.get_perms(self.user), set())

    def test_permissions_public_nonmember(self):
        """Test if the permissions are correct."""
        self.image_set.public = True
        self.image_set.save()
        self.assertEquals(self.image_set.get_perms(self.user), {
            'annotate',
            'delete_annotation',
            'edit_annotation',
            'read',
        })

    def test_permissions_nonpublic_member(self):
        """Test if the permissions are correct."""
        TeamMembership.objects.create(user=self.user, team=self.team)
        self.assertEquals(self.image_set.get_perms(self.user), {
            'annotate',
            'create_export',
            'delete_annotation',
            'delete_export',
            'delete_set',
            'edit_annotation',
            'edit_set',
            'read',
        })

    def test_permissions_public_member(self):
        """Test if the permissions are correct."""
        self.image_set.public = True
        self.image_set.save()
        TeamMembership.objects.create(user=self.user, team=self.team)
        self.assertEquals(self.image_set.get_perms(self.user), {
            'annotate',
            'create_export',
            'delete_annotation',
            'delete_export',
            'delete_set',
            'edit_annotation',
            'edit_set',
            'read',
        })

    def test_permissions_nonpublic_admin(self):
        """Test if the permissions are correct."""
        TeamMembership.objects.create(
            user=self.user, team=self.team, is_admin=True)
        self.assertEquals(self.image_set.get_perms(self.user), {
            'annotate',
            'create_export',
            'delete_annotation',
            'delete_export',
            'edit_annotation',
            'edit_set',
            'read',
        })

    def test_permissions_public_admin(self):
        """Test if the permissions are correct."""
        self.image_set.public = True
        self.image_set.save()
        TeamMembership.objects.create(user=self.user, team=self.team, is_admin=True)
        self.assertEquals(self.image_set.get_perms(self.user), {
            'annotate',
            'create_export',
            'delete_annotation',
            'delete_export',
            'edit_annotation',
            'edit_set',
            'read',
        })
