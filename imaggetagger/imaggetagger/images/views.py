from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from .models import ImageSet, Image, AnnotationType, Annotation, Export, Verification
from django.conf import settings
from django.db.models import Q
import json
from datetime import datetime


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(str('/images/'))


def export_auth_view(request, export_id):
    if request.user.is_authenticated():
        return HttpResponse('authenticated')
    return HttpResponseForbidden('authentication denied')


@login_required
def index(request):
    # needed to show the list of the users imagesets
    imagesets = ImageSet.objects.all()
    return TemplateResponse(request, 'images/index.html', {
                            'image_sets': imagesets,
                            'usergroups': request.user.groups.all(),
                            })


@login_required
def overview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    # images the imageset contains
    images = Image.objects.filter(image_set=imageset)
    # the saved exports of the imageset
    exports = Export.objects.filter(image_set=image_set_id).order_by('-id')[:5]
    # a list of annotation types used in the imageset
    annotation_types = set()
    annotations = set()
    for image in images:
        annotations = annotations.union(Annotation.objects.filter(image=image))
    annotation_types = annotation_types.union([annotation.type for annotation in annotations])
    first_annotation = annotations.pop()
    return TemplateResponse(request, 'images/overview.html', {
                            'images': images,
                            'imageset': imageset,
                            'annotationtypes': annotation_types,
                            'first_annotation': first_annotation,
                            'exports': exports,
                            })


@login_required
def tagview(request, image_id):
    # here the stuff we got via POST gets put in the DB
    last_annotation_type_id = -1
    if request.method == 'POST' and verify_bounding_box_annotation(request.POST):
        vector_text = json.dumps({'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']})
        last_annotation_type_id = request.POST['selected_annotation_type']
        annotation = Annotation(vector=vector_text,
                                image=get_object_or_404(Image, id=request.POST['image_id']),
                                type=get_object_or_404(AnnotationType,
                                                       id=request.POST['selected_annotation_type']))
        annotation.user = (request.user if request.user.is_authenticated() else None)
        if 'not_in_image' in request.POST:
            annotation.not_in_image = 1  # 0 by default
        annotation.save()
        # the creator of the annotation verifies it instantly
        user_verify(request.user, annotation, True)
    annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
    selected_image = get_object_or_404(Image, id=image_id)
    set_images = Image.objects.filter(image_set=selected_image.image_set)\
        .order_by('name')

    # detecting next and last image in the set
    next_image = Image.objects.filter(image_set=selected_image.image_set)\
        .filter(id__gt=selected_image.id).order_by('id')
    if len(next_image) == 0:
        next_image = None
    else:
        next_image = next_image[0]
    last_image = Image.objects.filter(image_set=selected_image.image_set)\
        .filter(id__lt=selected_image.id).order_by('-id')
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
def tageditview(request, annotation_id):
    annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
    annotation = get_object_or_404(Annotation, id=annotation_id)
    selected_image = get_object_or_404(Image, id=annotation.image.id)
    set_images = Image.objects.filter(image_set=selected_image.image_set)
    vector = json.loads(annotation.vector)
    current_annotation_type_id = annotation.type.id
    return TemplateResponse(request, 'images/tageditview.html', {
                            'selected_image': selected_image,
                            'set_images': set_images,
                            'annotation_types': annotation_types,
                            'annotation': annotation,
                            'current_annotation_type_id': current_annotation_type_id,
                            'x1': vector['x1'],
                            'y1': vector['y1'],
                            'x2': vector['x2'],
                            'y2': vector['y2'],
                            })


@login_required
def tagdeleteview(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    image_id = annotation.image.id
    annotation.delete()
    print('deleted annotation ', annotation_id)
    return HttpResponseRedirect(str('/images/tagview/' + str(image_id) + '/'))


@login_required
def tageditsaveview(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.method == 'POST' and verify_bounding_box_annotation(request.POST):
        vector_text = json.dumps({
            'x1': request.POST['x1Field'],
            'y1': request.POST['y1Field'],
            'x2': request.POST['x2Field'],
            'y2': request.POST['y2Field']})
        annotation.vector = vector_text
        annotation.last_change_time = datetime.now()
        annotation.last_editor = (request.user if request.user.is_authenticated() else None)
        annotation.type = get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])
        annotation.verified_by.clear()
        if 'not_in_image' in request.POST:
            annotation.not_in_image = 1
        else:
            annotation.not_in_image = 0
        annotation.save()
        user_verify(request.user, annotation, True)
    return HttpResponseRedirect(str('/images/tagview/' + str(annotation.image.id) + '/'))


@login_required
def exportview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    images = Image.objects.filter(image_set=imageset)
    annotation_types = set()
    for image in images:
        annotation_types = annotation_types.union([annotation.type for annotation in Annotation.objects.filter(image=image)])
    return TemplateResponse(request, 'images/exportview.html', {
                            'imageset': imageset,
                            'annotationtypes': annotation_types,
                            })


@login_required
def exportcreateview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if request.method == 'POST':
        export_format = request.POST['export_format']
        if export_format == 'Bit-Bot AI':
            export_text, annotation_count = bitbotai_export(imageset)
            export = Export(type="Bit-BotAI",
                            image_set=imageset,
                            user=(request.user if request.user.is_authenticated() else None),
                            annotation_count=annotation_count,
                            export_text=export_text)
            export.save()
    return HttpResponseRedirect(str('/images/overview/' + str(image_set_id) + '/'))


@login_required
def exportdownloadview(request, export_id):
    db_export = get_object_or_404(Export, id=export_id)
    export = db_export.export_text
    response = HttpResponse(export, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + export_id + '_export.txt"'
    return response


@login_required
def annotationmanageview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    images = Image.objects.filter(image_set=imageset)
    annotations = Annotation.objects.filter(image__in=images)\
                                    .order_by('image_id')
    return TemplateResponse(request, 'images/annotationmanageview.html', {
                            'selected_image_set': imageset,
                            'image_sets': ImageSet.objects.all(),
                            'annotations': annotations})


@login_required
def userview(request, user_id):
    user = get_object_or_404(User, id=user_id)
    groups = user.groups.all()

    # todo: count the points
    points = 0

    return TemplateResponse(request, 'images/userview.html', {
                            'user': user,
                            'usergroups': groups,
                            'userpoints': points, })


@login_required
def groupview(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.user_set.all()
    return TemplateResponse(request, 'images/groupview.html', {
                            'group': group,
                            'memberset': members, })


@login_required
def creategroupview(request):
    name = request.POST['groupname']
    if len(name) <= 20 and len(name) >= 3:
        group = Group()
        group.name = name
        group.save()
        group.user_set.add(request.user)
        group.save()
        return HttpResponseRedirect(reverse('images_groupview', args=(group.id,)))
    return HttpResponseRedirect(str('/images/'))

@login_required
def verifyview(request, annotation_id):
    # here the stuff we got via POST gets put in the DB
    if request.method == 'POST':  # TODO get shit working
        annotation = get_object_or_404(Annotation, id=request.POST['annotation'])
        if request.POST['state'] == 'accept':
            state = True
            user_verify(request.user, annotation, state)
        elif request.POST['state']:
            state = False
            user_verify(request.user, annotation, state)
    annotation = get_object_or_404(Annotation, id=annotation_id)
    image = get_object_or_404(Image, id=annotation.image.id)
    vector = json.loads(annotation.vector)
    set_images = Image.objects.filter(image_set=image.image_set)
    set_annotations = Annotation.objects.filter(image__in=set_images)\
        .order_by('id')  # good... hopefully
    unverified_annotations = set_annotations.filter(~Q(user=request.user))
    # detecting next and last image in the set
    next_annotation = set_annotations.filter(id__gt=annotation.id).order_by('id')
    if len(next_annotation) == 0:
        next_annotation = None
    else:
        next_annotation = next_annotation[0]
    last_annotation = set_annotations.filter(id__lt=annotation.id).order_by('-id')
    if len(last_annotation) == 0:
        last_annotation = None
    else:
        last_annotation = last_annotation[0]
    next_unverified_annotation = unverified_annotations.filter(id__gt=annotation.id).order_by('id')
    if len(next_unverified_annotation) == 0:
        next_unverified_annotation = None
    else:
        next_unverified_annotation = next_unverified_annotation[0]
    last_unverified_annotation = unverified_annotations.filter(id__lt=annotation.id).order_by('-id')
    if len(last_unverified_annotation) == 0:
        last_unverified_annotation = None
    else:
        last_unverified_annotation = last_unverified_annotation[0]

    return TemplateResponse(request, 'images/verificationview.html', {
                            'image': image,
                            'annotation': annotation,
                            'next_annotation': next_annotation,
                            'next_unverified_annotation': next_unverified_annotation,
                            'last_annotation': last_annotation,
                            'last_unverified_annotation': last_unverified_annotation,
                            'set_annotations': set_annotations,
                            'first_annotation': set_annotations[0],
                            'unverified_annotations': unverified_annotations,
                            'annotation_x': vector['x1'],
                            'annotation_y': vector['y1'],
                            'width': int(vector['x2']) - int(vector['x1']),
                            'height': int(vector['y2']) - int(vector['y1']),
                            })


# helping function to create the Bot-Bot AI export
def bitbotai_export(imageset):
    images = Image.objects.filter(image_set=imageset)
    annotation_counter = 0
    a = []
    a.append('Export of Imageset ' +
             imageset.name +
             ' (ball annotations in bounding boxes)\n')
    a.append(settings.EXPORT_SEPARATOR.join([
        'imagename',
        'x1',
        'y1',
        'x2',
        'y2\n']))
    annotations = Annotation.objects.filter(image__in=images,
                                            type__name='ball')
    for annotation in annotations:
        annotation_counter += 1
        vector = json.loads(annotation.vector)
        a.append(settings.EXPORT_SEPARATOR.join([annotation.image.name,
                                                vector['x1'],
                                                vector['y1'],
                                                vector['x2'],
                                                (vector['y2'] + '\n')]))
    return ''.join(a), annotation_counter


def user_verify(user, annotation, verification_state):
    if user.is_authenticated():
        Verification.objects.filter(user=user, annotation=annotation).delete()
        verification = Verification(user=user,
                                    annotation=annotation, verified=verification_state)
        verification.save()


def verify_bounding_box_annotation(post_dict):
    return ('not_in_image' in post_dict) or ((int(post_dict['x2Field']) - int(post_dict['x1Field'])) > 10 and (int(post_dict['y2Field']) - int(post_dict['y1Field'])) > 10)
