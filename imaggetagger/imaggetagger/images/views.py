from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse

from .models import ImageSet


#@login_required
def index(request):
    imagesets = ImageSet.objects.all()
    return TemplateResponse(request, 'images/index.html', {
                                'imagesets': imagesets,
                            })


def overview(request, imageset_id):
    pass