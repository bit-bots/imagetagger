from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, F, Subquery, OuterRef, IntegerField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime
from imagetagger.annotations.models import Verification, Annotation, ExportFormat
from imagetagger.annotations.forms import ExportFormatEditForm
from imagetagger.images.forms import ImageSetCreationForm
from imagetagger.images.models import ImageSet
from imagetagger.users.forms import RegistrationForm, TeamCreationForm
from .models import Team, TeamMembership


@login_required
def create_team(request):
    form = TeamCreationForm()
    if request.method == 'POST':
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.instance.save()
                form.instance.memberships.create(user=request.user,
                                                 is_admin=True)
            return redirect(reverse('users:team', args=(form.instance.id,)))
    return render(request, 'users/create_team.html', {
        'form': form,
    })


@login_required
@require_POST
def revoke_team_admin(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)

    if user == request.user:
        messages.warning(
            request, _('You can not revoke your own admin privileges.').format(
                team.name))
        return redirect(reverse('users:team', args=(team.id,)))

    if team.has_perm('user_management', request.user):
        team.memberships.filter(user=user).update(is_admin=False)
    else:
        messages.warning(
            request,
            _('You do not have permission to revoke this users admin '
              'privileges in the team {}.').format(team.name))

    return redirect(reverse('users:team', args=(team.id,)))


@login_required
@require_POST
def grant_team_admin(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)

    if not team.members.filter(pk=request.user.pk).exists():
        messages.warning(request, _('You are no member of the team {}.').format(
            team.name))
        return redirect(reverse('users:explore_team'))

    # Allow granting of admin privileges any team member if there is no admin
    if team.has_perm('user_management', request.user) or not team.admins:
        team.memberships.filter(user=user).update(is_admin=True)
    else:
        messages.warning(
            request,
            _('You do not have permission to grant this user admin '
              'privileges in the team {}.').format(team.name))
    return redirect(reverse('users:team', args=(team.id,)))


@login_required
def explore_team(request):
    teams = Team.objects.all()

    query = request.GET.get('query')
    if query:
        teams = teams.filter(name__icontains=query)

    return render(request, 'base/explore.html', {
        'mode': 'team',
        'teams': teams,
    })


@login_required
def explore_user(request):
    users = User.objects.annotate(points=Subquery(
        Verification.objects.filter(
            verified=True,
            annotation__user_id=OuterRef('pk'))
        .values('annotation__user_id')
        .annotate(count=Count('annotation__user_id'))
        .values('count'), output_field=IntegerField())).all()\
        .order_by(F('points').desc(nulls_last=True)).distinct()

    query = request.GET.get('query')
    if query:
        users = users.filter(username__icontains=query)

    return render(request, 'base/explore.html', {
        'mode': 'user',
        'users': users,
    })


@login_required
def leave_team(request, team_id, user_id=None):
    team = get_object_or_404(Team, id=team_id)

    user = request.user
    warning = _('You are not in the team.')

    try:
        user_id = int(user_id)
    except ValueError:
        return redirect(reverse('users:team', args=(team.id,)))

    if user_id and user_id != request.user.pk:
        user = get_object_or_404(User, id=user_id)
        warning = _('The user is not in the team.')

        if not team.has_perm('user_management', request.user):
            messages.warning(
                request,
                _('You do not have the permission to kick other users from this team.'))
            return redirect(reverse('users:team', args=(team.id,)))

    if not team.members.filter(pk=user.pk).exists():
        messages.warning(request, warning)
        return redirect(reverse('users:team', args=(team.id,)))

    if request.method == 'POST':
        team.memberships.filter(user=user).delete()
        if team.memberships.count() is 0:
            for imageset in ImageSet.objects.filter(team=team):
                imageset.public = True
                imageset.image_lock = True
                imageset.save()
            team.delete()
        if user == request.user:
            return redirect(reverse('users:explore_team'))
        return redirect(reverse('users:team', args=(team.id,)))

    return render(request, 'users/leave_team.html', {
        'user': user,
        'team': team,
        'last': team.memberships.count() is 1,
    })


@require_POST
@login_required
def add_team_member(request: HttpRequest, team_id: int) -> HttpResponse:
    """Add a member to a team."""
    team = get_object_or_404(Team, id=team_id)

    username = request.POST.get('username')

    if not team.has_perm('user_management', request.user):
        messages.warning(
            request, _(
                'You do not have the permission to add users to the team {}.')
            .format(team.name))
        return redirect(reverse('users:team', args=(team_id,)))

    user = User.objects.filter(username=username).first()
    if not user:
        messages.warning(request, _('The user {} does not exist.')
                         .format(username))
        return redirect(reverse('users:team', args=(team_id,)))

    if team.members.filter(pk=user.pk).exists():
        messages.info(request, _(
            'The user {} is already a member of the team {}.').format(
            username, team.name))
        return redirect(reverse('users:team', args=(team_id,)))

    team.memberships.create(user=user)

    messages.success(request,
                     _('The user {} has been added to the team successfully.')
                     .format(username))

    return redirect(reverse('users:team', args=(team_id,)))


@login_required
def view_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all().annotate(points=Subquery(
        Verification.objects.filter(
            verified=True,
            annotation__user_id=OuterRef('pk'))
        .values('annotation__user_id')
        .annotate(count=Count('annotation__user_id'))
        .values('count'), output_field=IntegerField())).all()\
        .order_by(F('points').desc(nulls_last=True)).distinct()
    members_30 = team.members.all().annotate(points=Subquery(
        Verification.objects.filter(
            verified=True,
            annotation__user_id=OuterRef('pk'),
            annotation__time__gte=timezone.now() - datetime.timedelta(days=30))
        .values('annotation__user_id')
        .annotate(count=Count('annotation__user_id'))
        .values('count'), output_field=IntegerField())).filter(points__gt=0)\
        .order_by(F('points').desc(nulls_last=True)).distinct()

    is_member = request.user in members
    admins = team.admins
    imagesets = ImageSet.objects.filter(team=team).order_by('-public', 'name')
    export_formats = ExportFormat.objects.filter(team=team).order_by('name')
    export_format_forms = [ExportFormatEditForm(instance=format_instance) for format_instance in export_formats]
    if not is_member:
        imagesets = imagesets.filter(public=True)
    return render(request, 'users/view_team.html', {
        'team': team,
        'members': members,
        'members_30': members_30,
        'admins': admins,
        'imagesets': imagesets,
        'date_imagesets': imagesets.order_by('-time'),
        'size_imagesets': sorted(imagesets, key=lambda i: -i.image_count()),
        'test_imagesets': imagesets.filter(name__icontains='test'),
        'imageset_creation_form': ImageSetCreationForm(),
        'team_perms': team.get_perms(request.user),
        'export_formats_forms': zip(export_formats, export_format_forms),
    })


@login_required
def user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    teams = Team.objects.filter(members=user)

    # TODO: use a database trigger (after migrating to a custom user model for that)
    points = Verification.objects.filter(verified=True, annotation__user=user)\
        .count()

    return render(request, 'users/view_user.html', {
        'user': user,
        'teams': teams,
        'points': points,
    })
