from datetime import datetime

import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, \
    HTTP_403_FORBIDDEN

from imagetagger.annotations.forms import ExportFormatCreationForm
from imagetagger.annotations.models import Annotation, AnnotationType, Export, \
    Verification, ExportFormat
from imagetagger.annotations.serializers import AnnotationSerializer
from imagetagger.images.models import Image, ImageSet
from imagetagger.users.models import Team


def export_auth(request, export_id):
    if request.user.is_authenticated():
        return HttpResponse('authenticated')
    return HttpResponseForbidden('authentication denied')


@login_required
def annotate(request, image_id):
    selected_image = get_object_or_404(Image, id=image_id)
    imageset_perms = selected_image.image_set.get_perms(request.user)
    if 'read' in imageset_perms:
        # TODO: Make sure that integer coordinate values are stored in vector

        # here the stuff we got via POST gets put in the DB
        last_annotation_type_id = -1
        if request.method == 'POST' and request.POST.get("annotate") is not None:
            if 'annotate' in imageset_perms:
                try:
                    image = get_object_or_404(Image, id=request.POST['image_id'])
                    vector = {
                        'x1': int(request.POST['x1Field']),
                        'y1': int(request.POST['y1Field']),
                        'x2': int(request.POST['x2Field']),
                        'y2': int(request.POST['y2Field']),
                    }
                    if 'not_in_image' in request.POST:
                        vector = None
                except (KeyError, ValueError):
                    return HttpResponseBadRequest()

                if (vector is not None and
                        not Annotation.validate_vector(
                            vector, Annotation.VECTOR_TYPE.BOUNDING_BOX)):
                    messages.warning(request, _('No valid bounding box found.'))
                else:
                    last_annotation_type_id = request.POST['selected_annotation_type']
                    annotation_type = get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])
                    annotation = Annotation(
                        vector=vector, image=image, annotation_type=annotation_type,
                        user=request.user if request.user.is_authenticated() else None)

                    if not Annotation.similar_annotations(
                            vector, selected_image, annotation_type):
                        annotation.save()
                        # the creator of the annotation verifies it instantly
                        annotation.verify(request.user, True)
                    else:
                        messages.warning(request, "This tag already exists!")
            else:
                messages.warning(request, 'you do not have the permission to annotate in this imageset!')

        set_images = selected_image.image_set.images.all()
        annotation_types = AnnotationType.objects.filter(active=True)  # for the dropdown option

        filtered = request.GET.get("selected_annotation_type")
        new_filter = request.GET.get("filter")
        if filtered is not None:
            # filter images for missing annotationtype
            set_images = set_images.exclude(annotations__annotation_type_id=filtered)
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
            'imageset_perms': imageset_perms,
            'next_image': next_image,
            'last_image': last_image,
            'set_images': set_images,
            'annotation_types': annotation_types,
            'image_annotations': Annotation.objects.filter(
                image=selected_image).select_related(),
            'last_annotation_type_id': int(last_annotation_type_id),
            'filtered' : filtered,
            'vector_fields': (
                'x1',
                'x2',
                'y1',
                'y2',
            ),
        })
    else:
        return redirect(reverse('images:view_imageset', args=(selected_image.image_set.id,)))


@login_required
def edit_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.user is annotation.user or annotation.image.image_set.has_perm('edit_annotation', request.user):
        prev_page = request.META.get('HTTP_REFERER')
        prev_view = 0
        if prev_page:
            if 'verify' in prev_page:
                prev_view = 1
            elif 'manage' in prev_page:
                prev_view = 2
        else:
            prev_view = 2

        annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
        selected_image = get_object_or_404(Image, id=annotation.image.id)
        set_images = Image.objects.filter(image_set=selected_image.image_set)
        current_annotation_type_id = annotation.annotation_type.id
        return render(request, 'annotations/edit_annotation.html', {
            'selected_image': selected_image,
            'set_images': set_images,
            'annotation_types': annotation_types,
            'annotation': annotation,
            'current_annotation_type_id': current_annotation_type_id,
            'prev_page': prev_page,
            'prev_view': prev_view
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
    prev_view = request.GET.get("prev_view")
    if prev_view == '1':
        go_to = reverse('annotations:verify', args=(annotation.image.id,))
    elif prev_view == '2':
        go_to = reverse('annotations:manage_annotations', args=(annotation.image.image_set.id,))
    else:
        go_to = reverse('annotations:annotate', args=(annotation.id,))

    # TODO: Give feedback in case of missing permissions
    if request.method == 'POST' and (
                request.user is annotation.user or
                annotation.image.image_set.has_perm('edit_annotation', request.user)):
        try:
            annotation.vector = {
                'x1': request.POST['x1Field'],
                'y1': request.POST['y1Field'],
                'x2': request.POST['x2Field'],
                'y2': request.POST['y2Field'],
            }
            if 'not_in_image' in request.POST:
                annotation.vector = None
            annotation.last_change_time = datetime.now()
            annotation.last_editor = (request.user if request.user.is_authenticated() else None)
            annotation.annotation_type = get_object_or_404(AnnotationType, id=request.POST['selected_annotation_type'])
        except (KeyError, ValueError):
            return HttpResponseBadRequest()

        if not Annotation.validate_vector(annotation.vector, Annotation.VECTOR_TYPE.BOUNDING_BOX):
            messages.warning(request, _('No valid bounding box found.'))
            return redirect(go_to)

        if Annotation.similar_annotations(
                annotation.vector, annotation.image,
                annotation.annotation_type, exclude={annotation.pk}):
            messages.info(
                request,
                _('A similar annotation already exists. The edited annotation was deleted.'))
            annotation.delete()
            return redirect(go_to)

        with transaction.atomic():
            annotation.verified_by.clear()
            annotation.save()
            annotation.verify(request.user, True)
    return redirect(go_to)


@login_required
def create_export(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if imageset.has_perm('create_export', request.user):
        export = request.POST.get('export')
        if request.method == 'POST' and export is not None:
            selected_format = request.POST['export_format']
            format = get_object_or_404(ExportFormat, id=selected_format)
            export_text, annotation_count, export_filename = export_format(format, imageset)

            export = Export(image_set=imageset,
                            user= request.user,
                            annotation_count=annotation_count,
                            export_text=export_text,
                            format=format)
            export.save()
            export.filename = export_filename.replace('%%exportid', str(export.id))
            export.save()

    return redirect(reverse('images:view_imageset', args=(image_set_id,)))


@login_required
def download_export(request, export_id):
    db_export = get_object_or_404(Export, id=export_id)
    export = db_export.export_text
    response = HttpResponse(export, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(db_export.filename)
    return response


@login_required
def manage_annotations(request, image_set_id):
    userteams = Team.objects.filter(members=request.user)
    imagesets = ImageSet.objects.select_related('team').filter(
        Q(team__in=userteams) | Q(public=True))
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    images = Image.objects.filter(image_set=imageset)
    annotations = Annotation.objects.annotate_verification_difference() \
        .select_related('image', 'user', 'last_editor',
                        'annotation_type').filter(image__in=images) \
        .order_by('id')
    return render(request, 'annotations/manage_annotations.html', {
        'selected_image_set': imageset,
        'image_sets': imagesets,
        'annotations': annotations,
    })

@login_required
def verify(request, annotation_id):
    # here the stuff we got via POST gets put in the DB
    if request.method == 'POST' and request.POST.get("annotation") is not None:
        annotation = get_object_or_404(Annotation, id=request.POST['annotation'])
        if not annotation.image.image_set.has_perm('verify', request.user):
            messages.warning(request, "You have no permission to verify this tag!")
            return HttpResponseForbidden()
        if request.POST['state'] == 'accept':
            state = True
            annotation.verify(request.user, state)
            messages.success(request, "You verified the last tag to be true!")
        elif request.POST['state'] == 'reject':
            state = False
            annotation.verify(request.user, state)
            messages.success(request, "You verified the last tag to be false!")

    annotation = get_object_or_404(
        Annotation.objects.select_related(), id=annotation_id)
    if not annotation.image.image_set.has_perm('verify', request.user):
        messages.warning(request, "You have no permission to verify this tag!")
        return redirect(
            reverse('images:view_imageset', args=(annotation.image.image_set.id,)))

    # checks if user has already verified this tag
    if Verification.objects.filter(user=request.user, annotation=annotation).count() > 0:
        messages.add_message(request, messages.WARNING, 'You have already verified this tag!')

    annotation_type = annotation.annotation_type
    image = get_object_or_404(Image, id=annotation.image.id)
    set_images = Image.objects.filter(image_set=image.image_set)
    set_annotations = Annotation.objects.select_related().filter(image__in=set_images)
    set_annotations = set_annotations.order_by('id')

    # filtering of annotations for certain annotations types
    # and/or ones that the user has already verified
    user_veri = request.GET.get("filter_veri")
    veri_pushed = request.GET.get("filter_button")
    annotation_types = AnnotationType.objects.filter(active=True) #for the dropdown option
    filtered = request.GET.get("selected_annotation_type")
    new_filter = request.GET.get("filter")
    if filtered is not None and user_veri is not None:
        # filters for both annotation type and not verified by user
        set_annotations = set_annotations.filter(
            ~Q(verified_by=request.user), annotation_type_id=filtered)
        if not set_annotations:
            # if there are no search results the search will be resetted
            messages.info(request, 'There are no unverified tags of this type in this set!')
            set_annotations = Annotation.objects.filter(image__in=set_images)
            filtered = None
            user_veri = None
        if new_filter is not None or veri_pushed is not None:
            # sets the current viewed annotation to the one on top of the filtered list
            annotation = set_annotations[0]
    elif filtered is not None:
        # filters annotations for certain types
        set_annotations = set_annotations.filter(annotation_type_id=filtered)
        if not set_annotations:
            # if there are no search results the search will be resetted
            messages.info(request, 'There are no tags of this type in this set!')
            set_annotations = Annotation.objects.filter(image__in=set_images)
            filtered = None
        if new_filter is not None:
            # sets the current viewed annotation to the one on top of the filtered list
            annotation = set_annotations[0]
    elif user_veri is not None:
        # filters for not verified annotations for user
        set_annotations = set_annotations.exclude(verified_by=request.user)
        if not set_annotations:
            # if there are no search results the search will be resetted
            messages.info(request, 'There are no unverified tags in this set!')
            set_annotations = Annotation.objects.filter(image__in=set_images)
            user_veri = None
        if veri_pushed is not None:
            # sets the current viewed annotation to the one on top of the filtered list
            annotation = set_annotations[0]

    unverified_annotations = set_annotations.exclude(verified_by=request.user)

    # TODO: Use one query to fetch all those previous's and next's

    # detecting next and last image in the set
    next_annotation = set_annotations.filter(id__gt=annotation.id).order_by('id').first()
    last_annotation = set_annotations.filter(id__lt=annotation.id).order_by('id').last()

    # detecting next and last unverified image in the set
    next_unverified_annotation = unverified_annotations.filter(id__gt=annotation.id).order_by('id').first()
    last_unverified_annotation = unverified_annotations.filter(id__lt=annotation.id).order_by('id').last()
    try:
        filtered = int(filtered)
    except (ValueError, TypeError):
        pass
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
        'width': annotation.vector.get('x2', 0) - annotation.vector.get('x1', 0) if annotation.vector else None,
        'height': annotation.vector.get('y2', 0) - annotation.vector.get('y1', 0) if annotation.vector else None,
        'annotation_type': annotation_type,
        'annotation_types': annotation_types,
        'filtered': filtered,
        'user_veri': user_veri,
        'veri_pushed': veri_pushed,
        'last_annotation_type_id': filtered
    })


# TODO secure that only logged in users can use this
def export_format(export_format_name, imageset):
    images = Image.objects.filter(image_set=imageset)
    export_format = export_format_name
    file_name = export_format.name_format

    placeholders_filename = {
        '%%imageset': imageset.name,
        '%%team': imageset.team.name,
        '%%setlocation': imageset.location,
    }
    for key, value in placeholders_filename.items():
                        file_name = file_name.replace(key, str(value))

    min_verifications = export_format.min_verifications
    annotation_counter = 0

    if export_format_name.image_aggregation:
        image_content = '\n'
        for image in images:
            annotations = Annotation.objects.annotate_verification_difference()\
                .filter(image=image,
                        verification_difference__gte=min_verifications,
                        annotation_type__in=export_format.annotations_types.all())
            if annotations:
                annotation_content = ''
                for annotation in annotations:
                    annotation_counter += 1
                    if annotation.not_in_image:
                        formatted_annotation = export_format.not_in_image_format
                        placeholders_annotation = {
                            '%%imageset': imageset.name,
                            '%%imagewidth': annotation.image.width,
                            '%%imageheight': annotation.image.height,
                            '%%imagename': image.name,
                            '%%type': annotation.annotation_type.name,
                            '%%veriamount': annotation.verification_difference,
                        }
                    else:
                        formatted_annotation = export_format.annotation_format
                        placeholders_annotation = {
                            '%%imageset': imageset.name,
                            '%%imagewidth': image.width,
                            '%%imageheight': image.height,
                            '%%imagename': image.name,
                            '%%type': annotation.annotation_type.name,
                            '%%veriamount': annotation.verification_difference,
                            # absolute values
                            '%%x1': annotation.vector['x1'],
                            '%%x2': annotation.vector['x2'],
                            '%%y1': annotation.vector['y1'],
                            '%%y2': annotation.vector['y2'],
                            '%%rad': annotation.radius,
                            '%%dia': annotation.diameter,
                            '%%cx': annotation.center['xc'],
                            '%%cy': annotation.center['yc'],
                            '%%width': annotation.width,
                            '%%height': annotation.height,
                            # relative values
                            '%%relx1': annotation.relative_vector['x1'],
                            '%%relx2': annotation.relative_vector['x2'],
                            '%%rely1': annotation.relative_vector['y1'],
                            '%%rely2': annotation.relative_vector['y2'],
                            '%%relrad': annotation.relative_radius,
                            '%%reldia': annotation.relative_diameter,
                            '%%relcx': annotation.relative_center['xc'],
                            '%%relcy': annotation.relative_center['yc'],
                            '%%relwidth': annotation.relative_width,
                            '%%relheight': annotation.relative_height,
                        }
                    for key, value in placeholders_annotation.items():
                        formatted_annotation = formatted_annotation\
                            .replace(key, str(value))
                    annotation_content += formatted_annotation + '\n'

                formatted_image = export_format.image_format
                placeholders_image = {
                    '%%imageset': imageset.name,
                    '%%imagewidth': image.width,
                    '%%imageheight': image.height,
                    '%%imagename': image.name,
                    '%%annotations': annotation_content,
                    '%%annoamount': annotations.count(),
                }
                for key, value in placeholders_image.items():
                    formatted_image = formatted_image.replace(key, str(value))
                image_content += formatted_image + '\n'
        formatted_content = image_content
    else:
        annotations = Annotation.objects.annotate_verification_difference()\
            .filter(image__in=images,
                    verification_difference__gte=min_verifications,
                    annotation_type__in=export_format.annotations_types.all())
        annotation_content = '\n'
        for annotation in annotations:
            annotation_counter += 1
            if annotation.not_in_image:
                formatted_annotation = export_format.not_in_image_format
                placeholders_annotation = {
                    '%%imageset': imageset.name,
                    '%%imagewidth': annotation.image.width,
                    '%%imageheight': annotation.image.height,
                    '%%imagename': annotation.image.name,
                    '%%type': annotation.annotation_type.name,
                    '%%veriamount': annotation.verification_difference,
                }
            else:
                formatted_annotation = export_format.annotation_format
                placeholders_annotation = {
                    '%%imageset': imageset.name,
                    '%%imagewidth': annotation.image.width,
                    '%%imageheight': annotation.image.height,
                    '%%imagename': annotation.image.name,
                    '%%type': annotation.annotation_type.name,
                    '%%veriamount': annotation.verification_difference,
                    # absolute values
                    '%%x1': annotation.vector['x1'],
                    '%%x2': annotation.vector['x2'],
                    '%%y1': annotation.vector['y1'],
                    '%%y2': annotation.vector['y2'],
                    '%%rad': annotation.radius,
                    '%%dia': annotation.diameter,
                    '%%cx': annotation.center['xc'],
                    '%%cy': annotation.center['yc'],
                    '%%width': annotation.width,
                    '%%height': annotation.height,
                    # relative values
                    '%%relx1': annotation.relative_vector['x1'],
                    '%%relx2': annotation.relative_vector['x2'],
                    '%%rely1': annotation.relative_vector['y1'],
                    '%%rely2': annotation.relative_vector['y2'],
                    '%%relrad': annotation.relative_radius,
                    '%%reldia': annotation.relative_diameter,
                    '%%relcx': annotation.relative_center['xc'],
                    '%%relcy': annotation.relative_center['yc'],
                    '%%relwidth': annotation.relative_width,
                    '%%relheight': annotation.relative_height,
                }
            for key, value in placeholders_annotation.items():
                formatted_annotation = formatted_annotation.replace(key, str(value))
            annotation_content = annotation_content + formatted_annotation + '\n'
        formatted_content = annotation_content
    base_format = export_format.base_format
    placeholders_base = {
        '%%content': formatted_content,
        '%%imageset': imageset.name,
        '%%setdescription': imageset.description,
        '%%team': imageset.team.name,
        '%%setlocation': imageset.location,
    }
    for key, value in placeholders_base.items():
        base_format = base_format.replace(key, str(value))
    return base_format, annotation_counter, file_name


@login_required
def create_exportformat(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    # TODO: permission for ExportFormats??

    if request.method == 'POST':
        form = ExportFormatCreationForm(request.POST)

        if form.is_valid():
            if ExportFormat.objects.filter(name=form.cleaned_data.get('name')).exists():
                form.add_error(
                    'name',
                    _('The name is already in use by an export format.'))
            else:
                with transaction.atomic():

                    form.save()

                messages.success(request, _('The export format was created successfully.'))
                return redirect(reverse('images:view_imageset', args=(imageset_id,)))
    else:
        form = ExportFormatCreationForm()
    return render(request, 'annotations/create_exportformat.html', {
        'imageset': imageset,
        'form': form,
    })


@login_required
@api_view(['DELETE'])
def api_delete_annotation(request) -> Response:
    try:
        annotation_id = int(request.query_params['annotation_id'])
    except (KeyError, TypeError, ValueError):
        raise ParseError

    annotation = get_object_or_404(
        Annotation.objects.select_related(), pk=annotation_id)

    if not annotation.image.image_set.has_perm('delete_annotation', request.user):
        return Response({
            'detail': 'permission for deleting annotations in this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    image = annotation.image
    annotation.delete()

    serializer = AnnotationSerializer(
        image.annotations.select_related() \
            .order_by('annotation_type__name'), many=True)
    return Response({
        'annotations': serializer.data,
    }, status=HTTP_200_OK)




@login_required
@api_view(['POST'])
def create_annotation(request) -> Response:
    try:
        image_id = int(request.data['image_id'])
        annotation_type_id = int(request.data['annotation_type_id'])
        vector = request.data['vector']
    except (KeyError, TypeError, ValueError):
        raise ParseError

    image = get_object_or_404(Image, pk=image_id)
    annotation_type = get_object_or_404(AnnotationType, pk=annotation_type_id)

    if not image.image_set.has_perm('annotate', request.user):
        return Response({
            'detail': 'permission for annotating in this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    if not Annotation.validate_vector(vector, Annotation.VECTOR_TYPE.BOUNDING_BOX):
        return Response({
            'detail': 'the vector is invalid.'
        }, status=HTTP_400_BAD_REQUEST)

    if Annotation.similar_annotations(vector, image, annotation_type):
        return Response({
            'detail': 'similar annotation exists.',
        })

    with transaction.atomic():
        annotation = Annotation.objects.create(
            vector=vector, image=image,
            annotation_type=annotation_type, user=request.user)

        # Automatically verify for owner
        annotation.verify(request.user, True)

    serializer = AnnotationSerializer(
        annotation.image.annotations.select_related() \
            .order_by('annotation_type__name'), many=True)
    return Response({
        'annotations': serializer.data,
    }, status=HTTP_201_CREATED)


@login_required
@api_view(['GET'])
def load_annotations(request) -> Response:
    try:
        image_id = int(request.query_params['image_id'])
    except (KeyError, TypeError, ValueError):
        raise ParseError

    image = get_object_or_404(Image, pk=image_id)

    if not image.image_set.has_perm('read', request.user):
        return Response({
            'detail': 'permission for reading this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    serializer = AnnotationSerializer(
        image.annotations.select_related().order_by('annotation_type__name'),
        many=True)
    return Response({
        'annotations': serializer.data,
    }, status=HTTP_200_OK)


@login_required
@api_view(['POST'])
def update_annotation(request) -> Response:
    try:
        annotation_id = int(request.data['annotation_id'])
        image_id = int(request.data['image_id'])
        annotation_type_id = int(request.data['annotation_type_id'])
        vector = request.data['vector']
    except (KeyError, TypeError, ValueError):
        raise ParseError

    annotation = get_object_or_404(Annotation, pk=annotation_id)
    annotation_type = get_object_or_404(AnnotationType, pk=annotation_type_id)

    if annotation.image_id != image_id:
        raise ParseError('the image id does not match the annotation id.')

    if not annotation.image.image_set.has_perm('edit_annotation', request.user):
        return Response({
            'detail': 'permission for updating annotations in this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    if not Annotation.validate_vector(vector, Annotation.VECTOR_TYPE.BOUNDING_BOX):
        return Response({
            'detail': 'the vector is invalid.'
        }, status=HTTP_400_BAD_REQUEST)

    if Annotation.similar_annotations(
            vector, annotation.image, annotation_type, exclude={annotation.id}):
        annotation.delete()
        return Response({
            'detail': 'similar annotation exists.',
        })

    with transaction.atomic():
        annotation.annotation_type = annotation_type
        annotation.vector = vector
        annotation.last_editor = request.user
        annotation.save()
        annotation.annotation_type = annotation_type

        # Automatically verify for owner
        annotation.verify(request.user, True)

    serializer = AnnotationSerializer(
        annotation.image.annotations.select_related() \
            .order_by('annotation_type__name'), many=True)
    return Response({
        'annotations': serializer.data,
    }, status=HTTP_200_OK)
