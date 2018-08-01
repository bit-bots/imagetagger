from django.shortcuts import render
from django.conf import settings
from django.db import transaction
from imagetagger.tagger_messages.forms import TeamMessageCreationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def send_team_message(request):
    if request.method == 'POST':
        form = TeamMessageCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.instance.creator = request.user
                form.instance.save() #TODO fake
                form.instance.read_by.add(request.user)
                form.save()
            return redirect(request.POST['source'])
        messages.error(request, 'Invalid message form')
    if 'source' in request.POST:
        return redirect(request.POST['source'])
    else:
        return redirect(reverse('images:index'))
