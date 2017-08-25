import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from imagetagger.annotations.models import Annotation, AnnotationType, Export, \
    Verification
from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team


def export_auth(request, export_id):
    if request.user.is_authenticated():
        return HttpResponse('authenticated')
    return HttpResponseForbidden('authentication denied')


@login_required
def annotate(request, image_id):
    selected_image = get_object_or_404(Image, id=image_id)
    if selected_image.image_set.has_perm('annotate', request.user) or selected_image.image_set.public:
        # here the stuff we got via POST gets put in the DB
        last_annotation_type_id = -1
        if request.method == 'POST' and request.POST.get("annotate") is not None and verify_bounding_box_annotation(request.POST):
            vector = {'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']}
            vector_text = json.dumps({'x1': request.POST['x1Field'], 'y1': request.POST['y1Field'], 'x2': request.POST['x2Field'], 'y2': request.POST['y2Field']})
            last_annotation_type_id = request.POST['selected_annotation_type']
            annotation = Annotation(vector=vector_text,
                                    image=get_object_or_404(Image, id=request.POST['image_id']),
                                    type=get_object_or_404(AnnotationType,
                                                           id=request.POST['selected_annotation_type']))
            annotation.user = (request.user if request.user.is_authenticated() else None)
            if 'not_in_image' in request.POST:
                annotation.not_in_image = 1  # 0 by default
            #tests for duplicates of same tag type & similiar coordinates (+-5 on every coordinate) on image
            result = []
            for annota in Annotation.objects.filter(image=selected_image, type=last_annotation_type_id):
                anno_vector = json.loads(annota .vector)
                sum = 0
                for key, value in anno_vector.items():
                    if abs(int(value) - int(vector[key])) <= 5:
                        sum = sum + abs(int(value) - int(vector[key]))
                    else:
                        sum = sum + len(vector)*5 +1
                result.append(sum)
            if (not any(elem <= len(vector)*5 for elem in result)) or result == []:
                annotation.save()
                # the creator of the annotation verifies it instantly
                user_verify(request.user, annotation, True)
            else:
                messages.warning(request, "This tag already exists!")


        set_images = selected_image.image_set.images.all()
        annotation_types = AnnotationType.objects.filter(active=True)  # for the dropdown option
        filtered = request.GET.get("selected_annotation_type")
        new_filter = request.GET.get("filter")
        if filtered is not None:
            # filter images for missing annotationtype
            set_images = set_images.exclude(annotation__type_id=filtered)
            if not set_images:
                messages.info(request, 'All images in this set have been tagged with this tag!')
                set_images = Image.objects.filter(image_set=selected_image.image_set)
                filtered = None
            if new_filter is not None:
                # sets the current viewed image to the one on top of the filtered list
                selected_image = set_images[0]
        set_images = set_images.order_by('id')

        # detecting next and last image in the set
        next_image = set_images.filter(id__gt=selected_image.id).order_by('id').first()
        last_image = set_images.filter(id__lt=selected_image.id).order_by('id').last()

        return render(request, 'annotations/annotate.html', {
            'selected_image': selected_image,
            'next_image': next_image,
            'last_image': last_image,
            'set_images': set_images,
            'annotation_types': annotation_types,
            'image_annotations': Annotation.objects.filter(
                image=selected_image).select_related(),
            'last_annotation_type_id': int(last_annotation_type_id),
            'filtered' : filtered,
        })
    else:
        return redirect(reverse('images:view_imageset', args=(selected_image.image_set.id,)))


@login_required
def edit_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.user is annotation.user or annotation.image.image_set.has_perm('edit_annotation', request.user):
        annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
        selected_image = get_object_or_404(Image, id=annotation.image.id)
        set_images = Image.objects.filter(image_set=selected_image.image_set)
        vector = json.loads(annotation.vector)
        current_annotation_type_id = annotation.type.id
        return render(request, 'annotations/edit_annotation.html', {
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
    else:
        return redirect(reverse('annotations:annotate', args=(annotation.image.id,)))


@login_required
def delete_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if annotation.image.image_set.has_perm('delete_annotation', request.user):
        annotation.delete()
        print('deleted annotation ', annotation_id)
    return redirect(reverse('annotations:annotate', args=(annotation.image.id,)))


@login_required
def edit_annotation_save(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.method == 'POST' \
            and verify_bounding_box_annotation(request.POST) \
            and (request.user is annotation.user
                 or annotation.image.image_set.has_perm('edit_annotation', request.user)):
        vector_text = json.dumps({
            'x1': request.POST['x1Field'],
            'y1': request.POST['y1Field'],
            'x2': request.POST['x2Field'],
            'y2': request.POST['y2Field']
        })
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
    return redirect(reverse('annotations:annotate', args=(annotation.image.id,)))


@login_required
def create_export(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if imageset.has_perm('create_export', request.user) or imageset.public:
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
            if export_format == 'wf_wolves':
                export_text, annotation_count = wf_wolves_export(imageset)
                export = Export(type="WF-Wolves",
                                image_set=imageset,
                                user=(request.user if request.user.is_authenticated() else None),
                                annotation_count=annotation_count,
                                export_text=export_text)
                export.save()
    return redirect(reverse('images:view_imageset', args=(image_set_id,)))


@login_required
def download_export(request, export_id):
    db_export = get_object_or_404(Export, id=export_id)
    export = db_export.export_text
    response = HttpResponse(export, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + export_id + '_export.txt"'
    return response


@login_required
def manage_annotations(request, image_set_id):
    userteams = Team.objects.filter(members=request.user)
    imagesets = ImageSet.objects.filter(team__in=userteams) | ImageSet.objects.filter(public=True)
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    images = Image.objects.filter(image_set=imageset)
    annotations = Annotation.objects.filter(image__in=images) \
        .order_by('id')
    return render(request, 'annotations/manage_annotations.html', {
        'selected_image_set': imageset,
        'image_sets': imagesets,
        'annotations': annotations})

@login_required
def verify(request, annotation_id):
    # here the stuff we got via POST gets put in the DB
    if request.method == 'POST' and request.POST.get("annotation") is not None:
        annotation = get_object_or_404(Annotation, id=request.POST['annotation'])
        if request.POST['state'] == 'accept':
            state = True
            user_verify(request.user, annotation, state)
            messages.success(request, "You verified the last tag to be true!")
        elif request.POST['state'] == 'reject':
            state = False
            user_verify(request.user, annotation, state)
            messages.success(request, "You verified the last tag to be false!")

    annotation = get_object_or_404(
        Annotation.objects.select_related(), id=annotation_id)

    #checks if user has already verified this tag
    if Verification.objects.filter(user=request.user, annotation=annotation).count() > 0:
        messages.add_message(request, messages.WARNING, 'You have already verified this tag!')

    annotation_type = annotation.__getattribute__('type')
    image = get_object_or_404(Image, id=annotation.image.id)
    vector = json.loads(annotation.vector)

    #sets everthing without the filter
    set_images = Image.objects.filter(image_set=image.image_set)
    set_annotations = Annotation.objects.select_related().filter(image__in=set_images)

    #filtering of annotations for certain annotations types
    annotation_types = AnnotationType.objects.filter(active=True) #for the dropdown option
    filtered = request.GET.get("selected_annotation_type")
    new_filter = request.GET.get("filter")
    if filtered is not None:
        #filter images for missing annotationtype
        set_annotations = set_annotations.filter(type_id=filtered)
        if not set_annotations:
            messages.info(request, 'There are no tags of this type in this set!')
            set_annotations = Annotation.objects.filter(image__in=set_images)
            filtered = None
        if new_filter is not None:
            #sets the current viewed annotation to the one on top of the filtered list
            annotation = set_annotations[0]
    set_annotations = set_annotations.order_by('id')  # good... hopefully
    #filters the unverified annotations
    unverified_annotations = set_annotations.filter(~Q(verified_by=request.user))


    # TODO: Use one query to fetch all those previous's and next's

    # detecting next and last image in the set
    next_annotation = set_annotations.filter(id__gt=annotation.id).order_by('id').first()
    last_annotation = set_annotations.filter(id__lt=annotation.id).order_by('id').last()

    # detecting next and last unverified image in the set
    next_unverified_annotation = unverified_annotations.filter(id__gt=annotation.id).order_by('id').first()
    last_unverified_annotation = unverified_annotations.filter(id__lt=annotation.id).order_by('id').last()

    return render(request, 'annotations/verification.html', {
        'image': image,
        'annotation': annotation,
        'next_annotation': next_annotation,
        'next_unverified_annotation': next_unverified_annotation,
        'last_annotation': last_annotation,
        'last_unverified_annotation': last_unverified_annotation,
        'set_annotations': set_annotations,
        'first_annotation': set_annotations.first(),
        'unverified_annotations': unverified_annotations,
        'annotation_x': vector['x1'],
        'annotation_y': vector['y1'],
        'width': int(vector['x2']) - int(vector['x1']),
        'height': int(vector['y2']) - int(vector['y1']),
        'annotation_type': annotation_type,
        'annotation_types': annotation_types,
        'filtered': filtered
    })


# helping function to create the Bot-Bot AI export
def bitbotai_export(imageset):
    images = Image.objects.filter(image_set=imageset)
    annotation_counter = 0
    a = []
    a.append('# Export of Imageset ' +
             imageset.name +
             ' (ball annotations in bounding boxes)\n')
    a.append('# set[' +
             imageset.name +
             ']\n')
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


# helping function to create the Bot-Bot AI export
def wf_wolves_export(imageset):
    images = Image.objects.filter(image_set=imageset)
    annotation_counter = 0
    a = []
    a.append('# Export of Imageset ' +
             imageset.name +
             ' (all annotations in bounding boxes)\n')
    a.append('# set[' +
             imageset.name +
             ']\n')
    a.append(settings.EXPORT_SEPARATOR.join([
        'imagename',
        'annotationtype',
        'x1',
        'y1',
        'x2',
        'y2\n']))
    annotations = Annotation.objects.filter(image__in=images)
    for annotation in annotations:
        annotation_counter += 1
        vector = json.loads(annotation.vector)
        a.append(settings.EXPORT_SEPARATOR.join([annotation.image.name,
                                                 annotation.type.name,
                                                 vector['x1'],
                                                 vector['y1'],
                                                 vector['x2'],
                                                 (vector['y2'] + '\n')]))
    return ''.join(a), annotation_counter


def user_verify(user, annotation, verification_state):
    if user.is_authenticated():
        #if verication already exists it'll be updated otherwise a new one will be created
        if Verification.objects.filter(user=user, annotation=annotation).count() > 0:
            Verification.objects.filter(user=user, annotation=annotation).update(verified=verification_state)
        else:
            Verification(annotation=annotation, user=user, verified=verification_state).save()

def verify_bounding_box_annotation(post_dict):
    return ('not_in_image' in post_dict) or ((int(post_dict['x2Field']) - int(post_dict['x1Field'])) >= 1 and (int(post_dict['y2Field']) - int(post_dict['y1Field'])) >= 1)
