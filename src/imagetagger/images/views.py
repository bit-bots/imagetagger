from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.expressions import F
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse, \
    FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from json import JSONDecodeError
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, \
    HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from PIL import Image as PIL_Image

from imagetagger.images.serializers import ImageSetSerializer, ImageSerializer, SetTagSerializer
from imagetagger.images.forms import ImageSetCreationForm, ImageSetCreationFormWT, ImageSetEditForm
from imagetagger.users.forms import TeamCreationForm
from imagetagger.users.models import User, Team
from imagetagger.tagger_messages.forms import TeamMessageCreationForm
from imagetagger.base.filesystem import root, tmp

from .models import ImageSet, Image, SetTag
from .forms import LabelUploadForm
from imagetagger.annotations.models import Annotation, Export, ExportFormat, \
    AnnotationType, Verification
from imagetagger.tagger_messages.models import Message, TeamMessage, GlobalMessage

import string
import random
import hashlib
import json
import imghdr
from io import BytesIO
from datetime import date, timedelta
from fs.zipfs import ReadZipFS
from fs.errors import ResourceNotFound
from os.path import splitext


@login_required
def explore_imageset(request):
    imagesets = ImageSet.objects.select_related('team').order_by(
        'team__name', 'name').filter(
        Q(team__members=request.user) | Q(public=True)).distinct()

    query = request.GET.get('query')
    tagfilter = request.GET.get('tags')
    get_query = ''
    get_tagfilter = ''
    tag_names = None
    if query:
        imagesets = imagesets.filter(name__icontains=query)
        get_query = '&query=' + str(query)
    if tagfilter:
        tag_names = str(tagfilter).replace(' ', '').split(',')
        for tag_name in tag_names:
            if tag_name.replace(' ', ''):
                imagesets = imagesets.filter(set_tags__name=tag_name)
        get_tagfilter = '&tags=' + str(tagfilter)

    paginator = Paginator(imagesets, 25)
    page = request.GET.get('page')
    page_imagesets = paginator.get_page(page)

    return TemplateResponse(request, 'base/explore.html', {
        'mode': 'imageset',
        'imagesets': page_imagesets,  # to separate what kind of stuff is displayed in the view
        'paginator': page_imagesets,  # for page stuff
        'get_query': get_query,
        'get_tagfilter': get_tagfilter,
        'tagnames': tag_names,  # currently not used
        'tagfilter': tagfilter,
        'query': query,
    })


@login_required
def index(request):
    team_creation_form = TeamCreationForm()

    # needed to show the list of the users imagesets
    userteams = Team.objects.filter(members=request.user)
    # get all teams where the user is an admin
    user_admin_teams = Team.objects.filter(memberships__user=request.user, memberships__is_admin=True)
    imagesets = ImageSet.objects.filter(team__in=userteams).annotate(
        image_count_agg=Count('images')
    ).select_related('team').prefetch_related('set_tags') \
        .order_by('-priority', '-time')

    imageset_creation_form = ImageSetCreationFormWT()  # the user provides the team manually
    imageset_creation_form.fields['team'].queryset = userteams
    annotation_types = Annotation.objects.values('annotation_type').annotate(
        annotation_count=Count('pk'),
        public_annotation_count=Count('pk', filter=Q(image__image_set__public=True)),
        name=F('annotation_type__name')).order_by('-public_annotation_count')

    image_stats = Image.objects.aggregate(
        total_count=Count('pk'),
        public_count=Count('pk', filter=Q(image_set__public=True)))
    imageset_stats = ImageSet.objects.aggregate(
        total_count=Count('pk'),
        public_count=Count('pk', filter=Q(public=True)))
    user_stats = User.objects.aggregate(
        total_count=Count('pk'),
        active_count=Count('pk', filter=Q(points__gte=50)))
    team_stats = Team.objects.aggregate(
        total_count=Count('pk'),
        active_count=Count('pk', filter=Q(
            pk__in=Team.objects.filter(
                memberships__user__in=User.objects.filter(
                    points__gte=50)))))

    stats = {
        'all_images': image_stats.get('total_count', 0) or 0,
        'public_images': image_stats.get('public_count', 0) or 0,
        'all_imagesets': imageset_stats.get('total_count', 0) or 0,
        'public_imagesets': imageset_stats.get('public_count', 0) or 0,
        'all_users': user_stats.get('total_count', 0) or 0,
        'active_users': user_stats.get('active_count', 0) or 0,
        'all_teams': team_stats.get('total_count', 0) or 0,
        'active_teams': team_stats.get('active_count', 0) or 0,
        'annotation_types': annotation_types[:3],
    }

    global_annoucements = Message.in_range(GlobalMessage.get(request.user).filter(~Q(read_by=request.user)))

    # Inits message creation form
    team_message_creation_form = TeamMessageCreationForm(
        initial={
            'start_time': str(date.today()),
            'expire_time': str(date.today() + timedelta(days=settings.DEFAULT_EXPIRE_TIME)),
        })

    team_message_creation_form.fields['team'].queryset = user_admin_teams

    # Gets all unread messages
    usermessages = Message.in_range(TeamMessage.get_messages_for_user(request.user)).filter(~Q(read_by=request.user))

    too_many_massages = False

    front_page_messages = 5

    if usermessages.count() > front_page_messages:
        usermessages = usermessages[:front_page_messages]
        too_many_massages = True

    many_annoucements = False
    if global_annoucements.count() > 5:
        many_annoucements = True

    return TemplateResponse(request, 'images/index.html', {
        'user': request.user,
        'team_creation_form': team_creation_form,
        'imageset_creation_form': imageset_creation_form,
        'team_message_creation_form': team_message_creation_form,
        'image_sets': imagesets,
        'user_has_admin_teams': user_admin_teams.exists(),
        'userteams': userteams,
        'stats': stats,
        'usermessages': usermessages,
        'too_many_messages': too_many_massages,
        'many_annoucements': many_annoucements,
        'global_annoucements': global_annoucements,
    })


@login_required
@require_http_methods(["POST", ])
def upload_image(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    imageset_dir = root().makedirs(imageset.root_path(), recreate=True)
    if request.method == 'POST' \
            and imageset.has_perm('edit_set', request.user) \
            and not imageset.image_lock:
        if request.FILES is None:
            return HttpResponseBadRequest('Must have files attached!')
        json_files = []
        for uploaded_file in request.FILES.getlist('files[]'):
            error = {
                'duplicates': 0,
                'damaged': False,
                'directories': False,
                'exists': False,
                'unsupported': False,
                'zip': False,
            }
            magic_number = uploaded_file.read(4)
            uploaded_file.seek(0)  # reset file cursor to the beginning of the file
            if magic_number == b'PK\x03\x04':  # ZIP file magic number
                error['zip'] = True
                with ReadZipFS(uploaded_file) as zip_fs:
                    try:
                        # Deal with weird structure of zip files created with macOS Finder.
                        subfolder = zip_fs.listdir("__MACOSX")[0]
                        zip_fs = zip_fs.opendir(subfolder)
                    except ResourceNotFound:
                        pass
                    filenames = sorted(f for f in zip_fs.walk.files(path="", max_depth=0))
                    duplicate_count = 0
                    for filename in filenames:
                        image_file = zip_fs.open(filename, 'rb')
                        try:
                            if imghdr.what(image_file) in settings.IMAGE_EXTENSION:
                                image_file.seek(0)
                                # creates a checksum for image
                                fchecksum = hashlib.sha512()
                                while True:
                                    buf = image_file.read(10000)
                                    if not buf:
                                        break
                                    fchecksum.update(buf)
                                image_file.seek(0)
                                fchecksum = fchecksum.digest()
                                # Tests for duplicates in imageset
                                if Image.objects.filter(checksum=fchecksum,
                                                        image_set=imageset).count() == 0:
                                    (shortname, extension) = splitext(filename)
                                    img_fname = (''.join(shortname) + '_' +
                                                 ''.join(
                                                     random.choice(
                                                         string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                                     for _ in range(6)) + extension)
                                    try:
                                        with PIL_Image.open(image_file) as image:
                                            width, height = image.size
                                        image_file.seek(0)
                                        imageset_dir.upload(img_fname, image_file)
                                        # TODO rfrigg: Check if necessary
                                        # shutil.chown(file_new_path, group=settings.UPLOAD_FS_GROUP)
                                        new_image = Image(name=filename,
                                                          image_set=imageset,
                                                          filename=img_fname,
                                                          checksum=fchecksum,
                                                          width=width,
                                                          height=height
                                                          )
                                        new_image.save()
                                    except (OSError, IOError):
                                        error['damaged'] = True
                                else:
                                    duplicate_count = duplicate_count + 1
                            else:
                                error['unsupported'] = True
                        except IsADirectoryError:
                            error['directories'] = True
                        finally:
                            image_file.close()

                    if duplicate_count > 0:
                        error['duplicates'] = duplicate_count
            else:
                # creates a checksum for image
                fchecksum = hashlib.sha512()
                for chunk in uploaded_file.chunks():
                    fchecksum.update(chunk)
                fchecksum = fchecksum.digest()
                # tests for duplicats in  imageset
                if Image.objects.filter(checksum=fchecksum, image_set=imageset)\
                        .count() == 0:
                    fname = uploaded_file.name.split('.')
                    fname = ('_'.join(fname[:-1]) + '_' +
                             ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                     for _ in range(6)) + '.' + fname[-1])
                    image = Image(
                        name=uploaded_file.name,
                        image_set=imageset,
                        filename=fname,
                        checksum=fchecksum)
                    buffer = BytesIO()
                    for chunk in uploaded_file.chunks():
                        buffer.write(chunk)
                    buffer.seek(0)
                    # TODO rfrigg: Check if necessary
                    # shutil.chown(image.path(), group=settings.UPLOAD_FS_GROUP)
                    if imghdr.what(buffer) in settings.IMAGE_EXTENSION:
                        try:
                            buffer.seek(0)
                            with PIL_Image.open(buffer) as pil_image:
                                width, height = pil_image.size
                            image.height = height
                            image.width = width
                            image.save()
                            buffer.seek(0)
                            imageset_dir.upload(fname, buffer)
                        except (OSError, IOError):
                            error['damaged'] = True
                    else:
                        error['unsupported'] = True
                else:
                    error['exists'] = True
            errormessage = ''
            if error['zip']:
                errors = list()
                if error['directories']:
                    errors.append('directories')
                if error['unsupported']:
                    errors.append('unsupported files')
                if error['duplicates'] > 0:
                    errors.append(str(error['duplicates']) + ' duplicates')
                if error['damaged']:
                    errors.append('damaged files')
                if len(errors) > 0:
                    # Build beautiful error message
                    errormessage += ', '.join(errors) + ' in the archive have been skipped!'
                    p = errormessage.rfind(',')
                    if p != -1:
                        errormessage = errormessage[:p].capitalize() + ' and' + errormessage[p + 1:]
                    else:
                        errormessage = errormessage.capitalize()
            else:
                if error['unsupported']:
                    errormessage = 'This file type is unsupported!'
                elif error['damaged']:
                    errormessage = 'This file seems to be damaged!'
                elif error['exists']:
                    errormessage = 'This image already exists in the imageset!'
            if errormessage == '':
                json_files.append({'name': uploaded_file.name,
                                   'size': uploaded_file.size,
                                   # 'url': reverse('images_imageview', args=(image.id, )),
                                   # 'thumbnailUrl': reverse('images_imageview', args=(image.id, )),
                                   # 'deleteUrl': reverse('images_imagedeleteview', args=(image.id, )),
                                   # 'deleteType': "DELETE",
                                   })
            else:
                json_files.append({'name': uploaded_file.name,
                                   'size': uploaded_file.size,
                                   'error': errormessage,
                                   })

        return JsonResponse({'files': json_files})


# @login_required
# def imageview(request, image_id):
#     image = get_object_or_404(Image, id=image_id)
#     root().open(image.path(), "rb") as f:
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
        # Let nginx determine the Content-Type
        del response['Content-Type']
        response['X-Accel-Redirect'] = "/ngx_static_dn/{}".format(image.relative_path())
        response["Content-Length"] = root().getsize(image.path())
    else:
        bytes_io = BytesIO()
        root().download(image.path(), bytes_io)
        bytes_io.seek(0)
        response = FileResponse(bytes_io, content_type="image")
        response["Content-Length"] = bytes_io.getbuffer().nbytes
    return response


@login_required
def list_images(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if not imageset.has_perm('read', request.user):
        return HttpResponseForbidden()
    return TemplateResponse(request, 'images/imagelist.txt', {
        'images': imageset.images.all()
    })


@login_required
def delete_images(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if image.image_set.has_perm('delete_images', request.user) and not image.image_set.image_lock:
        root().remove(image.path())
        image.delete()
        next_image = request.POST.get('next-image-id', '')
        if next_image == '':
            return redirect(reverse('images:view_imageset', args=(image.image_set.id,)))
        else:
            return redirect(reverse('annotations:annotate', args=(next_image,)))


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
    annotations = Annotation.objects.filter(
        image__in=images,
        annotation_type__active=True).order_by('image__name', 'id')
    annotation_types = AnnotationType.objects.filter(annotation__image__image_set=imageset, active=True).distinct()\
        .annotate(count=Count('annotation'),
                  in_image_count=Count('annotation', filter=Q(annotation__vector__isnull=False)),
                  not_in_image_count=Count('annotation', filter=Q(annotation__vector__isnull=True)))
    first_annotation = annotations.first()
    user_teams = Team.objects.filter(members=request.user)
    imageset_edit_form = ImageSetEditForm(instance=imageset)
    imageset_edit_form.fields['main_annotation_type'].queryset = AnnotationType.objects.filter(active=True)
    return render(request, 'images/imageset.html', {
        'images': images,
        'annotationcount': annotations.count(),
        'imageset': imageset,
        'annotationtypes': annotation_types,
        'annotation_types': annotation_types,
        'all_annotation_types': all_annotation_types,
        'first_annotation': first_annotation,
        'exports': exports,
        'filtered': filtered,
        'edit_form': imageset_edit_form,
        'imageset_perms': imageset.get_perms(request.user),
        'export_formats': ExportFormat.objects.filter(Q(public=True) | Q(team__in=user_teams)),
        'label_upload_form': LabelUploadForm(),
        'upload_notice': settings.UPLOAD_NOTICE,
        'enable_zip_download': settings.ENABLE_ZIP_DOWNLOAD,
    })


@login_required
def create_imageset(request):
    team = get_object_or_404(Team, id=request.POST['team'])

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
                    form.instance.creator = request.user
                    form.instance.save()
                    form.instance.path = '{}_{}'.format(team.id,
                                                        form.instance.id)
                    form.instance.save()

                    # create a folder to store the images of the set
                    folder_path = form.instance.root_path()
                    root().makedirs(folder_path, recreate=True)
                    # TODO rfrigg: Check if necessary
                    # shutil.chown(folder_path, group=settings.UPLOAD_FS_GROUP)

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
        root().removetree(imageset.root_path())
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
def toggle_pin_imageset(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if 'read' in imageset.get_perms(request.user):
        if request.user in imageset.pinned_by.all():
            imageset.pinned_by.remove(request.user)
            imageset.save()
            messages.info(request, 'Removed \"{}\" from your pinned imagesets'
                          .format(imageset.name))
        else:
            imageset.pinned_by.add(request.user)
            imageset.save()
            messages.info(request, 'Added \"{}\" to your pinned imagesets'
                          .format(imageset.name))

    return redirect(reverse('images:view_imageset', args=(imageset_id,)))


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
            if line in ('', "b'\n'"):
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
                        except JSONDecodeError:
                            report_list.append("In image \"{}\" the annotation:"
                                               " \"{}\" was not accepted as valid JSON".format(line_frags[0], line_frags[2]))

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
                                'For the image ' + line_frags[0] + ' the annotation ' +
                                line_frags[2] + ' was too similar to an already existing one')
                    else:
                        error_count += 1
                        report_list.append(
                            'For the image ' + line_frags[0] + ' the annotation ' +
                            line_frags[2] + ' was not a valid vector or '
                            'bounding box for the annotation type'
                        )
                else:
                    error_count += 1
                    report_list.append(
                        'For the image ' + line_frags[0] + ' the annotation type \"' +
                        line_frags[1] + '\" does not exist in this ImageTagger')
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


def download_imageset_zip(request, image_set_id):
    """
    Get a zip archive containing the images of the imageset with id image_set_id.
    If the zip file generation is still in progress, a HTTP status 202 (ACCEPTED) is returned.
    For empty image sets, status 204 (NO CONTENT) is returned instead of an empty zip file.
    """
    image_set = get_object_or_404(ImageSet, id=image_set_id)

    if not settings.ENABLE_ZIP_DOWNLOAD:
        return HttpResponse(status=HTTP_404_NOT_FOUND)

    if not image_set.has_perm('read', request.user):
        return HttpResponseForbidden()

    if image_set.image_count == 0:
        # It should not be possible to download empty image sets. This
        # is already blocked in the UI, but it should also be checked
        # on the server side.
        return HttpResponse(status=HTTP_204_NO_CONTENT)

    if image_set.zip_state != ImageSet.ZipState.READY:
        return HttpResponse(content=b'Imageset is currently processed', status=HTTP_202_ACCEPTED)

    if settings.USE_NGINX_IMAGE_PROVISION:
        response = HttpResponse(content_type='application/zip')
        response['X-Accel-Redirect'] = "/ngx_static_dn/{0}".format(image_set.relative_zip_path())
    else:
        response = FileResponse(root().open(image_set.zip_path(), 'rb'), content_type='application/zip')

    response['Content-Length'] = root().getsize(image_set.zip_path())
    response['Content-Disposition'] = "attachment; filename={}".format(image_set.zip_name())
    return response


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


@login_required
@api_view(['POST'])
def tag_image_set(request) -> Response:
    try:
        image_set_id = int(request.data['image_set_id'])
        tag_name = str(request.data['tag_name']).lower()
    except (KeyError, TypeError, ValueError):
        raise ParseError
    image_set = get_object_or_404(ImageSet, pk=image_set_id)
    char_blacklist = [',', '&', '=', '?']
    for char in char_blacklist:
        tag_name = tag_name.replace(char, '')
    tag_name = tag_name.replace(' ', '_')

    if not image_set.has_perm('edit_set', request.user):
        return Response({
            'detail': 'permission for tagging this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    if image_set.set_tags.filter(name=tag_name).exists():
        return Response({
            'detail': 'imageset has the tag already.',
        }, status=HTTP_200_OK)

    # TODO: validate the name?
    # TODO: this in better?
    if SetTag.objects.filter(name=tag_name).exists():
        tag = SetTag.objects.get(name=tag_name)
    else:
        tag = SetTag(name=tag_name)
        # TODO this in better?
        tag.save()
    tag.imagesets.add(image_set)
    tag.save()

    serializer = SetTagSerializer(tag)

    return Response({
        'detail': 'tagged the imageset.',
        'tag': serializer.data,
    }, status=HTTP_201_CREATED)


@login_required
@api_view(['DELETE'])
def remove_image_set_tag(request) -> Response:
    try:
        image_set_id = int(request.data['image_set_id'])
        tag_name = str(request.data['tag_name']).lower()
    except (KeyError, TypeError, ValueError):
        raise ParseError
    image_set = get_object_or_404(ImageSet, pk=image_set_id)
    tag = get_object_or_404(SetTag, name=tag_name)

    if not image_set.has_perm('edit_set', request.user):
        return Response({
            'detail': 'permission for tagging this image set missing.',
        }, status=HTTP_403_FORBIDDEN)

    if tag not in image_set.set_tags.all():
        return Response({
            'detail': 'tag not in imageset tags',
        }, status=HTTP_200_OK)
    tag.imagesets.remove(image_set)
    serializer = SetTagSerializer(tag)
    serializer_data = serializer.data
    if not tag.imagesets.exists() and tag.name != 'test':
        tag.delete()
    else:
        tag.save()

    return Response({
        'detail': 'removed the tag.',
        'tag': serializer_data,
    }, status=HTTP_201_CREATED)


@login_required
@api_view(['GET'])
def autocomplete_image_set_tag(request) -> Response:
    try:
        tag_name_query = str(request.GET['query']).lower()
    except (KeyError, TypeError, ValueError):
        raise ParseError
    tag_suggestions = list(SetTag.objects.filter(name__startswith=tag_name_query))
    tag_suggestions.extend(list(SetTag.objects.filter(~Q(name__startswith=tag_name_query) & Q(name__contains=tag_name_query))))
    tag_suggestions = [tag_suggestion.name for tag_suggestion in tag_suggestions]
    print(tag_suggestions)

    return Response({
        'query': tag_name_query,
        'suggestions': tag_suggestions,
    }, status=HTTP_200_OK)
