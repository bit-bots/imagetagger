from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
# Create your views here.
from django.template.response import TemplateResponse
from .models import ImageSet, Image, AnnotationType, Annotation
import json


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
    if request.method == 'POST':
        vector_text = json.dumps({'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']})
        Annotation(vector=vector_text, image=get_object_or_404(Image, id=request.POST['image_id']),\
                   user=(request.user if request.user.is_authenticated() else None), type=get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])).save()

    selected_image = get_object_or_404(Image, id=image_id)
    set_images = Image.objects.filter(image_set=selected_image.image_set)
    next_image = Image.objects.filter(image_set=selected_image.image_set).filter(id__gt=selected_image.id).order_by('id')
    if len(next_image)==0:
        next_image=None
    else:
        next_image=next_image[0]
    last_image = Image.objects.filter(image_set=selected_image.image_set).filter(id__lt=selected_image.id).order_by('-id')
    if len(last_image)==0:
        last_image=None
    else:
        last_image=last_image[0]
    annotation_types = AnnotationType.objects.all() # needed to select the annotation in the drop-down-menu
    return TemplateResponse(request, 'images/tagview.html', {
                                'selected_image': selected_image,
                                'next_image': next_image,
                                'last_image': last_image,
                                'set_images': set_images,
                                'annotation_types': annotation_types,
                                'image_annotations': Annotation.objects.filter(image=selected_image)
                            })

def image_set_creator(request):
    return TemplateResponse(request, 'images/createset.html', {})

