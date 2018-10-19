from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from imagetagger.tagger_messages.models import Message, TeamMessage, GlobalMessage
from imagetagger.tagger_messages.forms import TeamMessageCreationForm, GlobalMessageCreationForm
from imagetagger.users.models import TeamMembership
from imagetagger.users.models import User, Team
from django.conf import settings


@require_POST
@login_required
def send_team_message(request):
    form = TeamMessageCreationForm(request.POST)
    if (form.is_valid() and TeamMembership.objects.filter(
            user=request.user, team=form.instance.team, is_admin=True
    ).exists()):
        with transaction.atomic():
            team_message = form.save(commit=False)
            team_message.creator = request.user
            team_message.save()
            team_message.read_by.add(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    messages.error(request, 'Invalid message form')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@staff_member_required
def send_global_message(request):
    if request.method == 'POST':
        form = GlobalMessageCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                team_message = form.save(commit=False)
                team_message.creator = request.user
                team_message.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.error(request, 'Invalid message form')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def read_message(request, message_id):
    message = Message.objects.get(id=message_id)
    message.read_by.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def read_all_messages(request):
    messages = Message.in_range(TeamMessage.get_messages_for_user(request.user)).filter(~Q(read_by=request.user))
    current_user = User.objects.get(username=request.user.username)
    current_user.read_messages.add(*messages)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def delete_message(request, message_id):
    if request.user.is_staff:
        Message.objects.get(id=message_id).delete()
    else:
        Message.objects.filter(id=message_id, creator=request.user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def overview_unread(request):
    usermessages_all = Message.in_range(TeamMessage.get_messages_for_user(request.user)).filter(~Q(read_by=request.user))
    usermessages = Message.in_range(usermessages_all)
    usermessages_expired = usermessages_all.filter(~Q(pk__in=usermessages))

    user_admin_teams = Team.objects.filter(memberships__user=request.user, memberships__is_admin=True)

    team_message_creation_form = TeamMessageCreationForm(
        initial={
            'start_time': str(date.today()),
            'expire_time': str(date.today() + timedelta(days=settings.DEFAULT_EXPIRE_TIME)),
        })
    team_message_creation_form.fields['team'].queryset = user_admin_teams

    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'unread',
        'usermessages': usermessages,
        'usermessages_expired': usermessages_expired,
        'team_message_creation_form': team_message_creation_form,
        'user_has_admin_teams': user_admin_teams.exists(),
    })


@login_required
def overview_all(request):
    # Gets all team messages for the user, even from the past and future
    usermessages_all = TeamMessage.get_messages_for_user(request.user)
    usermessages = Message.in_range(usermessages_all)
    usermessages_expired = usermessages_all.filter(~Q(pk__in=usermessages))

    user_admin_teams = Team.objects.filter(memberships__user=request.user, memberships__is_admin=True)

    team_message_creation_form = TeamMessageCreationForm(
        initial={
            'start_time': str(date.today()),
            'expire_time': str(date.today() + timedelta(days=settings.DEFAULT_EXPIRE_TIME)),
        })
    team_message_creation_form.fields['team'].queryset = user_admin_teams

    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'all',
        'usermessages': usermessages,
        'usermessages_expired': usermessages_expired,
        'team_message_creation_form': team_message_creation_form,
        'user_has_admin_teams': user_admin_teams.exists(),
    })


@login_required
def overview_sent(request):
    usermessages_all = TeamMessage.get_messages_for_user(request.user).filter(creator=request.user)
    usermessages = Message.in_range(usermessages_all)
    usermessages_expired = usermessages_all.filter(~Q(pk__in=usermessages))

    # get all teams where the user is an admin
    user_admin_teams = Team.objects.filter(memberships__user=request.user, memberships__is_admin=True)

    team_message_creation_form = TeamMessageCreationForm(
        initial={
            'start_time': str(date.today()),
            'expire_time': str(date.today() + timedelta(days=settings.DEFAULT_EXPIRE_TIME)),
        })
    team_message_creation_form.fields['team'].queryset = user_admin_teams

    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'sent',
        'usermessages': usermessages,
        'usermessages_expired': usermessages_expired,
        'team_message_creation_form': team_message_creation_form,
        'user_has_admin_teams': user_admin_teams.exists(),
    })


@login_required
def overview_global(request):
    user_admin_teams = Team.objects.filter(memberships__user=request.user, memberships__is_admin=True).exists()
    # Gets all global announcements for the user, even from the past and future
    global_annoucements_all = GlobalMessage.get(request.user)

    global_annoucements = Message.in_range(global_annoucements_all)
    global_annoucements_expired = global_annoucements_all.filter(~Q(pk__in=global_annoucements))

    global_message_creation_form = GlobalMessageCreationForm(
        initial={
            'start_time': str(date.today()),
            'expire_time': str(date.today() + timedelta(days=settings.DEFAULT_EXPIRE_TIME)),
        })

    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'global',
        'global_annoucements': global_annoucements,
        'global_annoucements_expired': global_annoucements_expired,
        'user': request.user,
        'global_message_creation_form': global_message_creation_form,
        'user_has_admin_teams': user_admin_teams,
    })
