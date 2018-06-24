from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK
from PIL import Image as PIL_Image

from imagetagger.images.forms import ImageSetCreationForm, ImageSetEditForm
from imagetagger.images.serializers import ImageSetSerializer, ImageSerializer
from imagetagger.users.forms import TeamCreationForm
from .models import ImageSet, Image
from .forms import LabelUploadForm
from imagetagger.annotations.models import Annotation, Export, ExportFormat, \
    AnnotationType, Verification

from imagetagger.users.models import Team
import os
import shutil
import string
import random
import zipfile
import hashlib
import json

@login_required
def explore_imageset(request):
    imagesets = ImageSet.objects.select_related('team').order_by(
        'team__name', 'name').filter(
        Q(team__members=request.user) | Q(public=True)).distinct()

    query = request.GET.get('query')
    get_query = ''
    if query:
        imagesets = imagesets.filter(name__icontains=query)
        get_query = '&query=' + str(query)
    paginator = Paginator(imagesets, 25)
    page = request.GET.get('page')
    page_imagesets = paginator.get_page(page)

    return TemplateResponse(request, 'base/explore.html', {
        'mode': 'imageset',
        'imagesets': page_imagesets,  # to separate what kind of stuff is displayed in the view
        'paginator': page_imagesets,  # for page stuff
        'get_query': get_query,
        'query': query,
    })


@login_required
def index(request):
    team_creation_form = TeamCreationForm()

    # needed to show the list of the users imagesets
    userteams = Team.objects.filter(members=request.user)
    imagesets = ImageSet.objects.annotate(
        image_count_agg=Count('images')
    ).select_related('team').filter(team__in=userteams).order_by('id')
    return TemplateResponse(
        request, 'images/index.html', {
            'team_creation_form': team_creation_form,
            'image_sets': imagesets,
            'userteams': userteams,
        })


@login_required
@require_http_methods(["POST", ])
def upload_image(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.method == 'POST' \
            and imageset.has_perm('edit_set', request.user) \
            and not imageset.image_lock:
        if request.FILES is None:
            return HttpResponseBadRequest('Must have files attached!')
        json_files = []
        for f in request.FILES.getlist('files[]'):
            fname = f.name.split('.')
            if fname[-1] == 'zip':
                zipname = ''.join(random.choice(string.ascii_uppercase +
                                                string.ascii_lowercase +
                                                string.digits)
                                  for _ in range(6)) + '.zip'
                if not os.path.exists(os.path.join(imageset.root_path(), 'tmp')):
                    os.makedirs(os.path.join(imageset.root_path(), 'tmp'))
                with open(os.path.join(imageset.root_path(), 'tmp', zipname), 'wb') as out:
                    for chunk in f.chunks():
                        out.write(chunk)
                # unpack zip-file
                zip_ref = zipfile.ZipFile(os.path.join(imageset.root_path(), 'tmp', zipname), 'r')
                zip_ref.extractall(os.path.join(imageset.root_path(), 'tmp'))
                zip_ref.close()
                # delete zip-file
                os.remove(os.path.join(imageset.root_path(), 'tmp', zipname))
                filenames = [f for f in os.listdir(os.path.join(imageset.root_path(), 'tmp'))]
                filenames.sort()
                duplicat_count = 0
                for filename in filenames:
                    (shortname, extension) = os.path.splitext(filename)
                    if extension.lower() in settings.IMAGE_EXTENSION:
                        # creates a checksum for image
                        fchecksum = hashlib.sha512()
                        file_path = os.path.join(imageset.root_path(), 'tmp', filename)
                        with open(file_path, 'rb') as fil:
                            while True:
                                buf = fil.read(10000)
                                if not buf:
                                    break
                                fchecksum.update(buf)
                        fchecksum = fchecksum.digest()
                        # Tests for duplicats in imageset
                        if Image.objects.filter(checksum=fchecksum,
                                                image_set=imageset).count() == 0:

                            img_fname = (''.join(shortname) + '_' +
                                         ''.join(
                                             random.choice(
                                                 string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                             for _ in range(6)) + extension)
                            with PIL_Image.open(file_path) as image:
                                width, height = image.size
                            file_new_path = os.path.join(imageset.root_path(), img_fname)
                            shutil.move(file_path, file_new_path)
                            shutil.chown(file_new_path, group=settings.UPLOAD_FS_GROUP)
                            new_image = Image(name=filename,
                                              image_set=imageset,
                                              filename=img_fname,
                                              checksum=fchecksum,
                                              width=width,
                                              height=height
                                              )
                            new_image.save()
                        else:
                            os.remove(os.path.join(imageset.root_path(), 
                                                   'tmp', filename))
                            duplicat_count = duplicat_count + 1
                if duplicat_count > 0:
                    messages.warning(request, 
                                     "Duplicates detected: " + str(duplicat_count))
            else:
                # creates a checksum for image
                fchecksum = hashlib.sha512()
                for chunk in f.chunks():
                    fchecksum.update(chunk)
                fchecksum = fchecksum.digest()
                # tests for duplicats in  imageset
                if Image.objects.filter(checksum=fchecksum, image_set=imageset)\
                        .count() == 0:
                    fname = ('_'.join(fname[:-1]) + '_' +
                             ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                     for _ in range(6)) + '.' + fname[-1])
                    image = Image(
                        name=f.name,
                        image_set=imageset,
                        filename=fname,
                        checksum=fchecksum)
                    with open(image.path(), 'wb') as out:
                        for chunk in f.chunks():
                            out.write(chunk)
                    shutil.chown(image.path(), group=settings.UPLOAD_FS_GROUP)
                    with PIL_Image.open(image.path()) as image_file:
                        width, height = image_file.size
                    image.height = height
                    image.width = width
                    image.save()
                else:
                    messages.warning(request, "This image already exists in this set!")
            json_files.append({'name': f.name,
                               'size': f.size,
                               # 'url': reverse('images_imageview', args=(image.id, )),
                               # 'thumbnailUrl': reverse('images_imageview', args=(image.id, )),
                               # 'deleteUrl': reverse('images_imagedeleteview', args=(image.id, )),
                               # 'deleteType': "DELETE",
                               })
        return JsonResponse({'files': json_files})


# @login_required
# def imageview(request, image_id):
#     image = get_object_or_404(Image, id=image_id)
#     with open(os.path.join(settings.IMAGE_PATH, image.path()), "rb") as f:
#         return HttpResponse(f.read(), content_type="image/jpeg")

@login_required
def view_image(request, image_id):
    """
    This view is to authenticate direct access to the images via nginx auth_request directive

    it will return forbidden on if the user is not authenticated
    """
    image = get_object_or_404(Image, id=image_id)
    if not image.image_set.has_perm('read', request.user):
        return HttpResponseForbidden()
    if settings.USE_NGINX_IMAGE_PROVISION:
        response = HttpResponse()
        response["Content-Disposition"] = "attachment; filename={0}".format(
                image.name)
        response['X-Accel-Redirect'] = "/ngx_static_dn/{0}".format(image.relative_path())
        return response
    with open(os.path.join(settings.IMAGE_PATH, image.path()), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")


@login_required
def list_images(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if not imageset.has_perm('read', request.user):
        return HttpResponseForbidden()
    return TemplateResponse(request, 'images/imagelist.txt', {
        'images': imageset.images.all()
    })


@login_required
# TODO: bad!!! (fix javascript upload to use csrf for deletion)
@csrf_exempt
@require_http_methods(["DELETE", ])
def delete_images(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if image.image_set.has_perm('edit_imageset', request.user):
        os.remove(os.path.join(settings.IMAGE_PATH, image.full_path()))
        image.delete()
        return JsonResponse({'files': [{image.name: True}, ]})


def count_annotations_of_type(annotations, annotation_type):
    annotations = annotations.filter(annotation_type=annotation_type)
    annotation_count = annotations.count()
    neg_annotation_count = annotations.filter(vector=None).count()
    return (
        annotation_type.name,
        annotation_count,
        annotation_count - neg_annotation_count,
        neg_annotation_count,
    )


@login_required
def view_imageset(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if not imageset.has_perm('read', request.user):
        messages.warning(request, 'you do not have the permission to access this imageset')
        return redirect(reverse('images:index'))
    # images the imageset contains
    images = Image.objects.filter(image_set=imageset).order_by('name')
    # the saved exports of the imageset
    exports = Export.objects.filter(image_set=image_set_id).order_by('-id')[:5]
    filtered = False
    form_filter = request.POST.get('filter')
    if request.method == "POST" and form_filter is not None:
        filtered = True
        # filter images for missing annotationtype
        images = images.exclude(
            annotations__annotation_type_id=request.POST.get("selected_annotation_type"))
    # a list of annotation types used in the imageset
    all_annotation_types = AnnotationType.objects.filter(active=True)
    annotation_types = set()
    annotations = Annotation.objects.select_related().filter(
        image__in=images,
        annotation_type__active=True).order_by("id")
    annotation_types = annotation_types.union(
        [annotation.annotation_type for annotation in annotations])
    annotation_type_count = sorted(list(
        map(
            lambda at: count_annotations_of_type(annotations, at),
            annotation_types)),
        key=lambda at_tuple: at_tuple[1],
        reverse=True)
    first_annotation = annotations.first()
    user_teams = Team.objects.filter(members=request.user)
    imageset_edit_form = ImageSetEditForm(instance=imageset)
    imageset_edit_form.fields['main_annotation_type'].queryset = AnnotationType.objects.filter(active=True)
    return render(request, 'images/imageset.html', {
        'images': images,
        'annotationcount': len(annotations),
        'imageset': imageset,
        'annotationtypes': annotation_types,
        'annotation_types': annotation_types,
        'all_annotation_types': all_annotation_types,
        'annotation_type_count': annotation_type_count,
        'first_annotation': first_annotation,
        'exports': exports,
        'filtered': filtered,
        'edit_form': imageset_edit_form,
        'imageset_perms': imageset.get_perms(request.user),
        'export_formats': ExportFormat.objects.filter(Q(public=True)|Q(team__in=user_teams)),
        'label_upload_form': LabelUploadForm(),
        'upload_notice': settings.UPLOAD_NOTICE,
    })


@login_required
def create_imageset(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not team.has_perm('create_set', request.user):
        messages.warning(
            request,
            _('You do not have permission to create image sets in the team {}.')
            .format(team.name))
        return redirect(reverse('users:team', args=(team.id,)))

    form = ImageSetCreationForm()

    if request.method == 'POST':
        form = ImageSetCreationForm(request.POST)

        if form.is_valid():
            if team.image_sets\
                    .filter(name=form.cleaned_data.get('name')).exists():
                form.add_error(
                    'name',
                    _('The name is already in use by an imageset of this team.'))
            else:
                with transaction.atomic():
                    form.instance.team = team
                    form.instance.save()
                    form.instance.path = '{}_{}'.format(team.id,
                                                        form.instance.id)
                    form.instance.save()

                    # create a folder to store the images of the set
                    folder_path = form.instance.root_path()
                    os.makedirs(folder_path)
                    shutil.chown(folder_path, group=settings.UPLOAD_FS_GROUP)

                messages.success(request,
                                 _('The image set was created successfully.'))
                return redirect(reverse('images:view_imageset',
                                        args=(form.instance.id,)))

    return render(request, 'images/create_imageset.html', {
        'team': team,
        'form': form,
    })


@login_required
def edit_imageset(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if not imageset.has_perm('edit_set', request.user):
        messages.warning(request,
                         _('You do not have permission to edit this imageset.'))
        return redirect(reverse('images:view_imageset', args=(imageset.id,)))

    form = ImageSetEditForm(instance=imageset)

    if request.method == 'POST':
        form = ImageSetEditForm(request.POST, instance=imageset)
        if form.is_valid():
            form.save()
            # TODO: check if name and path are unique in the team
            return redirect(reverse('images:view_imageset',
                                    args=(imageset.id,)))

    return render(request, 'images/edit_imageset.html', {
        'form': form,
    })


@login_required
def delete_imageset(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if not imageset.has_perm('delete_set', request.user):
        messages.warning(request,
                         _('You do not have permission to delete this imageset.'))
        return redirect(reverse('images:imageset', args=(imageset.pk,)))

    if request.method == 'POST':
        shutil.rmtree(imageset.root_path())
        imageset.delete()
        return redirect(reverse('users:team', args=(imageset.team.id,)))

    return render(request, 'images/delete_imageset.html', {
        'imageset': imageset,
    })

@login_required
def set_free(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if not imageset.images:
        messages.warning(request,
                         _('You can not release an empty imageset'))
        return redirect(reverse('images:imageset', args=(imageset.pk,)))
    if not imageset.has_perm('delete_set', request.user):
        messages.warning(request,
                         _('You do not have permission to release this imageset'))
        return redirect(reverse('images:imageset', args=(imageset.pk,)))

    if request.method == 'POST':
        imageset.public = True
        imageset.public_collaboration = True
        imageset.team = None
        imageset.image_lock = True
        imageset.save()
        return redirect(reverse('images:view_imageset', args=(imageset_id,)))
    return render(request, 'images/setfree_imageset.html', {
        'imageset': imageset,
    })

@login_required
def label_upload(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if not imageset.has_perm('annotate', request.user):
        messages.warning(request,
                         _('You do not have permission to upload the annotations to this set.'))
        return redirect(reverse('images:view_imageset', args=(imageset_id,)))

    images = Image.objects.filter(image_set=imageset)
    report_list = list()
    if request.method == 'POST':
        error_count = 0
        similar_count = 0
        verify = 'verify' in request.POST.keys()
        for line in request.FILES['file']:
            # filter empty lines
            print(line)
            if line in ('',  "b'\n'"):
                continue
            dec_line = line.decode().replace('\n', '').replace(',}', '}')
            line_frags = dec_line.split('|')
            image = images.filter(name=line_frags[0])
            if image.exists():
                image = image[0]
                annotation_type = AnnotationType.objects.filter(name=line_frags[1], active=True)
                if annotation_type.exists():
                    annotation_type = annotation_type[0]
                    vector = False
                    blurred = False
                    concealed = False
                    if len(line_frags) > 3:
                        flags = line_frags[3]
                        test_flags = flags.replace('b', '')
                        test_flags = test_flags.replace('c', '')
                        if len(test_flags) > 0:
                            report_list.append(
                                'unknown flags: \"{}\" for image: \"{}\"'
                                .format(test_flags, line_frags[0])
                            )
                        blurred = 'b' in flags
                        concealed = 'c' in flags
                    if line_frags[2] == 'not in image' or line_frags[2] == '{}':
                        vector = None

                    else:
                        try:
                            vector = json.loads(line_frags[2])
                        except Exception as error:
                            report_list.append("In image \"{}\" the annotation:"
                                        " \"{}\" was not accepted as valid JSON".format(line_frags[0],line_frags[2]))

                    if annotation_type.validate_vector(vector):
                        if not Annotation.similar_annotations(vector, image, annotation_type):
                            annotation = Annotation()
                            annotation.annotation_type = annotation_type
                            annotation.image = image
                            annotation.user = request.user
                            annotation.vector = vector
                            annotation._blurred = blurred
                            annotation._concealed = concealed
                            annotation.save()
                            if verify:
                                verification = Verification()
                                verification.user = request.user
                                verification.annotation = annotation
                                verification.verified = True
                                verification.save()
                        else:
                            similar_count += 1
                            report_list.append(
                                'For the image ' + line_frags[0] + ' the annotation '
                                + line_frags[2] + ' was too similar to an already existing one')
                    else:
                        error_count += 1
                        report_list.append(
                            'For the image ' + line_frags[0] + ' the annotation '
                            + line_frags[2] + ' was not a valid vector or '
                                            'bounding box for the annotation type'
                        )
                else:
                    error_count += 1
                    report_list.append(
                        'For the image ' + line_frags[0] + ' the annotation type \"'
                        + line_frags[1] + '\" does not exist in this ImageTagger')
            else:
                error_count += 1
                report_list.append('The image \"' + line_frags[0] + '\" does not exist in this imageset')

        for element in report_list[:20]:
            messages.error(request, element)
            if len(report_list) > 20:
                messages.warning(request, 'Only the first 20 errors are displayed.')
        if error_count + similar_count > 0:
            messages.warning(
                request,
                _('The label upload ended with {} errors and {} similar existing labels.')
                .format(error_count, similar_count))
        else:
            messages.success(
                request,
                _('The label upload ended with {} errors and {} similar existing labels.')
                .format(error_count, similar_count))
    return redirect(reverse('images:view_imageset', args=(imageset_id,)))


def dl_script(request):
    return TemplateResponse(request, 'images/download.py', context={
        'base_url': settings.DOWNLOAD_BASE_URL,
        }, content_type='text/plain')


@login_required
@api_view(['GET'])
def load_image_set(request) -> Response:
    try:
        image_set_id = int(request.query_params['image_set_id'])
        filter_annotation_type_id = request.query_params.get(
            'filter_annotation_type_id')
    except (KeyError, TypeError, ValueError):
        raise ParseError

    image_set = get_object_or_404(ImageSet, pk=image_set_id)

    if not image_set.has_perm('read', request.user):
        return Response({
            'detail': 'permission for reading this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    serializer = ImageSetSerializer(image_set)
    serialized_image_set = serializer.data
    if filter_annotation_type_id:
        filter_annotation_type = get_object_or_404(
            AnnotationType, pk=filter_annotation_type_id)
        # TODO: find a cleaner solution to filter related field set wihtin ImageSet serializer
        serialized_image_set['images'] = ImageSerializer(
            image_set.images.exclude(
                annotations__annotation_type=filter_annotation_type).order_by(
                'name'), many=True).data
    else:
        # TODO: find a cleaner solution to order related field set wihtin ImageSet serializer
        serialized_image_set['images'] = ImageSerializer(
            image_set.images.order_by('name'), many=True).data
    return Response({
        'image_set': serialized_image_set,
    }, status=HTTP_200_OK)





