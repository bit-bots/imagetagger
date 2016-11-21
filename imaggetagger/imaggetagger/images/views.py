from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.template.response import TemplateResponse

from .models import ImageSet, Image, AnnotationType


#@login_required
def index(request):
    imagesets = ImageSet.objects.all()
    return TemplateResponse(request, 'images/index.html', {
                                'image_sets': imagesets,
                            })


def overview(request, image_set_id):
    images = Image.objects.filter(image_set = image_set_id)
    return TemplateResponse(request, 'images/overview.html', {
                                'images': images,
                            })


def tagview(request, image_id):
    selected_image = get_object_or_404(Image, id = image_id)
    set_images = Image.objects.filter(image_set = selected_image.image_set)
    annotation_types = AnnotationType.objects.all() #needed to select the annotation in the drop-down-menu
    return TemplateResponse(request, 'images/tagview.html', {
                                'selected_image': selected_image,
                                'set_images': set_images,
                                'annotation_types' : annotation_types,
                            })

def image_set_creator(request):
    return TemplateResponse(request, 'images/createset.html', {})