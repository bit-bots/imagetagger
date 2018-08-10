from django.db import transaction
from imagetagger.tagger_messages.forms import TeamMessageCreationForm, GlobalMessageCreationForm
from imagetagger.tagger_messages.models import Message, TeamMessage, GlobalMessage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from imagetagger.users.models import TeamMembership

@login_required
def send_team_message(request):
    if request.method == 'POST':
        form = TeamMessageCreationForm(request.POST)
        if (form.is_valid() and TeamMembership.objects.filter(
                user=request.user, team=form.instance.team, is_admin=True
                ).exists()):
            with transaction.atomic():
                form.instance.creator = request.user
                form.instance.save()
            return redirect(request.POST['source'])
        messages.error(request, 'Invalid message form')
    if 'source' in request.POST:
        return redirect(request.POST['source'])
    return redirect(reverse('images:index'))

@staff_member_required
def send_global_message(request):
    if request.method == 'POST':
        form = GlobalMessageCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.instance.creator = request.user
                print(form)
                form.instance.save()
            return redirect(request.POST['source'])
        messages.error(request, 'Invalid message form')
    if 'source' in request.POST:
        return redirect(request.POST['source'])
    return redirect(reverse('images:index'))

@login_required
def read_message(request, message_id):
    message = Message.objects.get(id=message_id)
    message.read_by.add(request.user)
    message.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def delete_message(request, message_id):
    if request.user.is_staff:
        Message.objects.get(id=message_id).delete()
    else:
        Message.objects.filter(id=message_id, creator=request.user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def overview_unread(request):
    usermessages = Message.in_range(TeamMessage.get_messages_for_user(request.user)).filter(~Q(read_by=request.user))

    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'unread',
        'usermessages': usermessages,
    })

@login_required
def overview_all(request):
    usermessages = TeamMessage.get_messages_for_user(request.user)
    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'all',
        'usermessages': usermessages,
    })

@login_required
def overview_sent(request):
    usermessages = TeamMessage.get_messages_for_user(request.user).filter(creator=request.user)
    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'sent',
        'usermessages': usermessages,
    })

@login_required
def overview_global(request):
    global_annoucements = GlobalMessage.get(request.user)
    return TemplateResponse(request, 'tagger_messages/overview.html', {
        'mode': 'global',
        'global_annoucements': global_annoucements,
        'user': request.user,
    })