from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.template.response import TemplateResponse
from django.contrib import messages
from fs.errors import ResourceNotFound
from .models import Tool
from .forms import ToolUploadForm, FileUploadForm
from imagetagger.users.models import Team
from imagetagger.base.filesystem import root


def tools_enabled(in_function):
    if not settings.TOOLS_ENABLED:
        raise Http404
    return in_function


@tools_enabled
@login_required
def overview(request):
    tools = Tool.objects.select_related('team').order_by(
        'name').filter(
        Q(creator=request.user) | Q(team__members=request.user) | Q(public=True)).distinct()
    delete_tools = [tool.id for tool in tools if tool.has_perm('delete_tool', request.user)]
    edit_tools = [tool.id for tool in tools if tool.has_perm('edit_tool', request.user)]
    tool_form = ToolUploadForm()
    tool_form.fields['team'].queryset = Team.objects.filter(members=request.user)
    return TemplateResponse(request, 'overview.html', {
        'tools': tools,
        'edit_tools': edit_tools,
        'delete_tools': delete_tools,
        'form': tool_form,
        'file_form': FileUploadForm(),
        'tool_upload_notice': settings.TOOL_UPLOAD_NOTICE,
    })


@tools_enabled
@login_required
def create_tool(request):
    if request.method == 'POST':
        form = ToolUploadForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.instance
            # TODO: use team permissions
            if tool.team and request.user not in tool.team.members.all():
                messages.error(
                    request,
                    'You are not permitted to create tools for the team "{}".'
                        .format(tool.team.name))
                return redirect(reverse('tools:overview'))
            with transaction.atomic():
                tool.creator = request.user
                tool.save()
            tool.filename = '{}_{}'.format(tool.id,
                                           request.FILES['file'].name)
            tools_dir = root().makedirs(settings.TOOLS_PATH)
            with tools_dir.open(tool.filename, 'wb+') as f:
                for chunk in request.FILES['file']:
                    f.write(chunk)
            messages.success(request, 'The tool was successfully uploaded')
            tool.save()
            return redirect(reverse('tools:overview'))

    messages.error(request, 'There was an error with your upload. You can only upload files up to 2 MiB')
    return redirect(reverse('tools:overview'))


@tools_enabled
@login_required
def edit_tool(request, tool_id):
    if request.method == 'POST':
        tool = get_object_or_404(Tool, id=tool_id)
        changed_name = False
        changed_description = False
        changed_public = False
        changed_file = False
        public = 'public' in request.POST.keys()
        if tool.name != request.POST['name']:
            tool.name = request.POST['name']
            changed_name = True
        if tool.description != request.POST['description']:
            tool.description = request.POST['description']
            changed_description = True
        if tool.public != public:
            tool.public = public
            changed_public = True
        file_form = FileUploadForm(request.POST, request.FILES)
        if file_form.is_valid() and 'file' in request.FILES.keys():
            changed_file = True
            tools_dir = root().opendir(settings.TOOLS_PATH)
            old_name = tool.filename
            tool.filename = request.FILES['file'].name
            tools_dir.remove(old_name)
            with tools_dir.open(tool.filename, 'wb+') as f:
                for chunk in request.FILES['file']:
                    f.write(chunk)
        tool.save()
        msg = 'changed'
        if changed_name:
            msg += ' name'
        if changed_description:
            msg += ' description'
        if changed_public:
            msg += ' public status'
        if changed_file:
            msg += ' file'
        if not (changed_public or changed_description or changed_file or changed_name):
            msg += ' nothing'
        msg += ' in the tool'
        messages.warning(request, msg)
        return redirect(reverse('tools:overview'))


@tools_enabled
@login_required
def delete_tool(request, tool_id):
    if request.method == 'POST':
        tool = get_object_or_404(Tool, id=tool_id)
        if tool.has_perm('delete_tool', request.user):
            tools_dir = root().opendir(settings.TOOLS_PATH)
            try:
                tools_dir.remove(tool.filename)
            except ResourceNotFound:
                pass
            tool.delete()
        else:
            messages.error(request, 'You do not have the permission to delete the tool!')
    return redirect(reverse('tools:overview'))


@tools_enabled
@login_required
def download_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    if tool.has_perm('download_tool', request.user):
        tools_dir = root().opendir(settings.TOOLS_PATH)
        if tools_dir.isfile(tool.filename):
            with tools_dir.open(tool.filename, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application")
                response['Content-Disposition'] = 'attachment; filename=' + tool.filename
                return response
        else:
            messages.error(request, 'There was an error accessing the tool')
    else:
        messages.error(request, 'You do not have the permission to download the tool!')
    return redirect(reverse('tools:overview'))
