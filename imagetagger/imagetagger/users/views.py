from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from guardian.shortcuts import assign_perm

from imagetagger.images.models import ImageSet
from .models import Team


@login_required
def create_team(request):
    name = request.POST['teamname']
    if len(name) <= 20 and len(name) >= 3:
        members = Group(name=name+'_members')
        members.save()
        admins = Group(name=name+'_admins')
        admins.save()
        user = request.user
        members.user_set.add(user)
        members.save()
        admins.user_set.add(user)
        admins.save()
        team = Team()
        team.name = name
        team.members = members
        team.admins = admins
        team.website = ''
        team.save()
        assign_perm('user_management', team.admins, team)
        assign_perm('create_set', team.members, team)
        return redirect(reverse('users:team', args=(team.id,)))
    return redirect(reverse('users:create_team'))


@login_required
def dethrone(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)
    if request.user.has_perm('user_management', team):
        team.admins.user_set.remove(user)
    return redirect(reverse('users:team', args=(team.id,)))


@login_required
def enthrone(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)
    if request.user.has_perm('user_management', team) or 0 == len(team.admins.user_set.all()):
        team.admins.user_set.add(user)
    return redirect(reverse('users:team', args=(team.id,)))


@login_required
def explore_team(request):
    teams = Team.objects.all()
    if request.method == 'POST':
        teams = teams.filter(name__icontains=request.POST['searchquery'])

    return render(request, 'base/explore.html', {
        'mode': 'team',
        'teams': teams,
    })


@login_required
def explore_user(request):
    users = User.objects.all()
    if request.method == 'POST':
        users = users.filter(username__contains=request.POST['searchquery'])

    return render(request, 'base/explore.html', {
        'mode': 'user',
        'users': users,
    })


@login_required
def leave_team(request, team_id, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    team = get_object_or_404(Team, id=team_id)
    team.members.user_set.remove(user)
    team.admins.user_set.remove(user)
    return redirect(reverse('users:team', args=(team.id,)))


def logout_view(request):
    logout(request)
    return redirect(reverse('images:index'))


@login_required
def view_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST' and request.user.has_perm('user_management', team):
        user_to_add = User.objects.filter(username=request.POST['username'])[0]
        if user_to_add:
            team.members.user_set.add(user_to_add)

    members = team.members.user_set.all()
    is_member = request.user in members
    admins = team.admins.user_set.all()
    is_admin = request.user in admins  # The request.user is an admin of the team
    no_admin = len(admins) == 0  # Team has no admin, so every member can claim the Position
    imagesets = ImageSet.objects.filter(team=team)
    pub_imagesets = imagesets.filter(public=True).order_by('id')
    priv_imagesets = imagesets.filter(public=False).order_by('id')
    return render(request, 'users/view_team.html', {
        'team': team,
        'memberset': members,
        'is_member': is_member,
        'is_admin': is_admin,
        'no_admin': no_admin,
        'admins': admins,
        'pub_imagesets': pub_imagesets,
        'priv_imagesets': priv_imagesets,
    })


@login_required
def user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    userteams = Team.objects.filter(members__in=user.groups.all())

    # TODO: count the points
    points = 0

    return render(request, 'users/view_user.html', {
        'user': user,
        'userteams': userteams,
        'userpoints': points,
    })


@require_POST
def create_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    if User.objects.filter(Q(username=username) | Q(email=email)).exists():
        messages.warning(request, _('A user with that username or email address exists.'))
        return redirect(reverse('users:login'))
    user = User.objects.create_user(username=username, email=email, password=password)
    messages.success(request, _('Your account was successfully created.'))
    return redirect(reverse('users:user', args=(user.id,)))
