from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.db.models import Q
from imagetagger.tools.models import Tool


def tools_enabled(in_function):
    if not settings.TOOLS_ENABLED:
        raise Http404
    return in_function


@tools_enabled
@login_required
def overview(request):
    tools = Tool.objects.select_related('team').order_by(
        'name').filter(
        Q(team__members=request.user) | Q(public=True)).distinct()
    pass


@tools_enabled
@login_required
def create_tool(request):
    pass


@tools_enabled
@login_required
def edit_tool(request, tool_id):
    pass


@tools_enabled
@login_required
def delete_tool(request, tool_id):
    pass


@tools_enabled
@login_required
def download_tool(request, tool_id):
    pass
