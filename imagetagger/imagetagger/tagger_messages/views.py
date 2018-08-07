from django.db import transaction
from imagetagger.tagger_messages.forms import TeamMessageCreationForm, GlobalMessageCreationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
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
                # form.instance.read_by.add(request.user)
                #form.instance.save()
            return redirect(request.POST['source'])
        messages.error(request, 'Invalid message form')
    if 'source' in request.POST:
        return redirect(request.POST['source'])
    else:
        return redirect(reverse('images:index'))

@login_required
def send_global_message(request):
    if request.method == 'POST':
        form = GlobalMessageCreationForm(request.POST)
        if (form.is_valid() ): # TODO Check if creator is staff member
            form.instance.save()
            return redirect(request.POST['source'])
        messages.error(request, 'Invalid message form')
    if 'source' in request.POST:
        return redirect(request.POST['source'])
    else:
        return redirect(reverse('images:index'))