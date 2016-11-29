from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from .models import ImageSet, Image, AnnotationType, Annotation
import json

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(str('/images/'))

@login_required
def index(request):
    imagesets = ImageSet.objects.all()
    return TemplateResponse(request, 'images/index.html', {
                                'image_sets': imagesets,
                            })

@login_required
def overview(request, image_set_id):
    images = Image.objects.filter(image_set=image_set_id)
    return TemplateResponse(request, 'images/overview.html', {
                                'images': images,
                            })

@login_required
def tagview(request, image_id):
    # here the stuff we got via POST gets put in the DB
    last_annotation_type_id = -1
    if request.method == 'POST':
        vector_text = json.dumps({'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']})
        last_annotation_type_id = request.POST['selected_annotation_type']
        Annotation(vector=vector_text, image=get_object_or_404(Image, id=request.POST['image_id']),\
                   user=(request.user if request.user.is_authenticated() else None), type=get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])).save()

    annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
    selected_image = get_object_or_404(Image, id=image_id)
    set_images = Image.objects.filter(image_set=selected_image.image_set).order_by('name')

    # detecting next and last image in the set
    next_image = Image.objects.filter(image_set=selected_image.image_set).filter(id__gt=selected_image.id).order_by('id')
    if len(next_image) == 0:
        next_image = None
    else:
        next_image = next_image[0]
    last_image = Image.objects.filter(image_set=selected_image.image_set).filter(id__lt=selected_image.id).order_by('-id')
    if len(last_image) == 0:
        last_image = None
    else:
        last_image = last_image[0]

    return TemplateResponse(request, 'images/tagview.html', {
                                'selected_image': selected_image,
                                'next_image': next_image,
                                'last_image': last_image,
                                'set_images': set_images,
                                'annotation_types': annotation_types,
                                'image_annotations': Annotation.objects.filter(image=selected_image),
                                'last_annotation_type_id': int(last_annotation_type_id),
                            })

@login_required
def tageditview(request, image_id, annotation_id):
    annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
    selected_image = get_object_or_404(Image, id=image_id)
    set_images = Image.objects.filter(image_set=selected_image.image_set)
    vector = json.loads(get_object_or_404(Annotation, id=annotation_id).vector)
    current_annotation_type_id = get_object_or_404(Annotation, id=annotation_id).type.id
    print(vector['x1'])
    return TemplateResponse(request, 'images/tageditview.html', {
                                'selected_image': selected_image,
                                'set_images': set_images,
                                'annotation_types': annotation_types,
                                'annotation': annotation_id,
                                'current_annotation_type_id': current_annotation_type_id,
                                'x1': vector['x1'],
                                'y1': vector['y1'],
                                'x2': vector['x2'],
                                'y2': vector['y2'],
                            })

@login_required
def tagdeleteview(request, image_id, annotation_id):
    get_object_or_404(Annotation, id=annotation_id).delete()
    print('deleted annotation ', annotation_id)
    return HttpResponseRedirect(str('/images/tagview/' + str(image_id) + '/'))

@login_required
def tageditsaveview(request, image_id, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.method == 'POST':
        vector_text = json.dumps({'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']})
        annotation.vector=vector_text
        annotation.image=get_object_or_404(Image, id=request.POST['image_id'])
        annotation.user=(request.user if request.user.is_authenticated() else None)
        annotation.type=get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])
    annotation.save()
    print('edited annotation ', annotation_id)

@login_required
def exportview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id = image_set_id)
    images = Image.objects.filter(image_set = imageset)
    annotation_types = set()
    for image in images:
        annotation_types = annotation_types.union([annotation.type for annotation in Annotation.objects.filter(image = image)])
    return TemplateResponse(request, 'images/exportview.html', {
                                'imageset': imageset,
                                'annotationtypes': annotation_types,
                            })

@login_required
def exportcreateview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id = image_set_id)
    images = Image.objects.filter(image_set = imageset)
    annotation_types = set()
    for image in images:
        annotation_types = annotation_types.union([annotation.type for annotation in Annotation.objects.filter(image = image)])
    return HttpResponseRedirect(str('/images/export/' + str(image_id) + '/'))
