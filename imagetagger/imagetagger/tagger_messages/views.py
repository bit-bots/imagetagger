from django.db import transaction
from imagetagger.tagger_messages.forms import TeamMessageCreationForm, GlobalMessageCreationForm
from imagetagger.tagger_messages.models import Message
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
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
