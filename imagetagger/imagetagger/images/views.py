from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from .models import ImageSet, Image
from imagetagger.annotations.models import Annotation, Export
from imagetagger.users.models import Team
from django.conf import settings
from django.db.models import Q
import os
import shutil
import string
import random
import json
from datetime import datetime
from guardian.shortcuts import assign_perm
import zipfile
import hashlib



@login_required
def explore_imageset(request):
    userteams = Team.objects.filter(members__in=request.user.groups.all())
    imagesets = ImageSet.objects.filter(team__in=userteams) | ImageSet.objects.filter(public=True)
    if request.method == 'POST':
        imagesets = imagesets.filter(name__contains=request.POST['searchquery'])

    return TemplateResponse(request, 'base/explore.html', {
        'mode': 'imagesets',
        'imagesets': imagesets,
    })


@login_required
def index(request):
    # needed to show the list of the users imagesets
    userteams = Team.objects.filter(members__in=request.user.groups.all())
    imagesets = ImageSet.objects.filter(team__in=userteams).order_by('id')
    return TemplateResponse(
        request, 'images/index.html', {
            'image_sets': imagesets,
            'userteams': userteams,
        })


@login_required
@require_http_methods(["POST", ])
def upload_image(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.method == 'POST' and request.user.has_perm('edit_set', imageset) and not imageset.image_lock:
        if request.FILES is None:
            return HttpResponseBadRequest('Must have files attached!')
        json_files = []
        for f in request.FILES.getlist('files[]'):
            fname = f.name.split('.')
            if fname[-1] == 'zip':
                zipname = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) + '.zip'
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
                for filename in filenames:
                    (shortname, extension) = os.path.splitext(filename)
                    if(extension.lower() in settings.IMAGE_EXTENSION):
                        img_fname = (''.join(shortname) + '_' +
                                     ''.join(
                                         random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                         for _ in range(6)) + extension)
                        fchecksum = hashlib.sha512()
                        with open(os.path.join(imageset.root_path(), 'tmp', filename), 'rb') as fil:
                            while True:
                                buf = fil.read(10000)
                                if not buf:
                                    break
                                fchecksum.update(buf)
                        fchecksum = fchecksum.digest()
                        if Image.objects.filter(checksum=fchecksum, image_set=imageset).count() == 0:
                            shutil.move(os.path.join(imageset.root_path(), 'tmp', filename), os.path.join(imageset.root_path(), img_fname))
                            Image(name=filename, image_set=imageset, filename=img_fname, checksum=fchecksum).save()
                        else:
                            os.remove(os.path.join(imageset.root_path(), 'tmp', filename))
            else:
                fname = ('_'.join(fname[:-1]) + '_' +
                         ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                 for _ in range(6)) + '.' + fname[-1])
                fchecksum = hashlib.sha512()
                for chunk in f.chunks():
                    fchecksum.update(chunk)
                fchecksum = fchecksum.digest()
                if Image.objects.filter(checksum=fchecksum, image_set=imageset).count() == 0:

                    image = Image(name=f.name, image_set=imageset, filename=fname, checksum=fchecksum)
                    image.save()
                    with open(image.path(), 'wb') as out:
                        for chunk in f.chunks():
                            out.write(chunk)
            json_files.append({'name': f.name,
                               'size': f.size,
                               # 'url': reverse('images_imageview', args=(image.id, )),
                               #'thumbnailUrl': reverse('images_imageview', args=(image.id, )),
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
    if not (image.image_set.public or request.user.has_perm('read', image.image_set)):
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
    if not (imageset.public or request.user.has_perm('read', imageset)):
        return HttpResponseForbidden()
    return TemplateResponse(request, 'images/imagelist.txt', {
        'images': imageset.image_set.all()
    })



@login_required
@csrf_exempt
@require_http_methods(["DELETE", ])
def delete_images(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.user.has_perm('edit_imageset', image.image_set):
        os.remove(os.path.join(settings.IMAGE_PATH, image.full_path()))
        image.delete()
        return JsonResponse({'files': [{image.name: True}, ]})


@login_required
def view_imageset(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    # images the imageset contains
    images = Image.objects.filter(image_set=imageset).order_by('id')
    # the saved exports of the imageset
    exports = Export.objects.filter(image_set=image_set_id).order_by('-id')[:5]
    # a list of annotation types used in the imageset
    annotation_types = set()
    annotations = Annotation.objects.filter(image__in=images)
    annotation_types = annotation_types.union([annotation.type for annotation in annotations])
    first_annotation = None
    if len(annotations) > 0:
        first_annotation = annotations[0]
    return TemplateResponse(request, 'images/imageset.html', {
                            'images': images,
                            'annotationcount': len(annotations),
                            'imageset': imageset,
                            'annotationtypes': annotation_types,
                            'first_annotation': first_annotation,
                            'exports': exports,
                            })


@login_required
@require_http_methods(["POST", ])
def create_imageset(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user.has_perm('create_set', team):
        # todo: check if name and path are unique in the team
        name = request.POST["name"]
        location = request.POST["location"]
        imageset = ImageSet(name=name, location=location, description='')
        imageset.public = "public" in request.POST
        imageset.save()
        imageset.path = '_'.join((str(team.id), str(imageset.id)))  # todo: some formatting would be great
        imageset.team = team
        imageset.save()
        os.makedirs(imageset.root_path())  # create a folder to store the images of the set
        assign_perm('edit_set', team.members, imageset)
        assign_perm('delete_set', team.admins, imageset)
        assign_perm('edit_annotation', team.members, imageset)
        assign_perm('delete_annotation', team.members, imageset)
        assign_perm('annotate', team.members, imageset)
        assign_perm('read', team.members, imageset)
        assign_perm('create_export', team.members, imageset)
        assign_perm('delete_export', team.members, imageset)
        return HttpResponseRedirect(reverse('images:view_imageset', args=(imageset.id,)))
    return HttpResponseRedirect(reverse('users:team', args=(team.id,)))


@login_required
@require_http_methods(["POST", ])
def edit_imageset(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.user.has_perm('edit_set', imageset):
        # todo: check if name and path are unique in the team
        imageset.name = request.POST["name"]
        imageset.location = request.POST["location"]
        imageset.description = request.POST["description"]
        imageset.public = "public" in request.POST
        imageset.image_lock = "image-lock" in request.POST
        imageset.save()
    return HttpResponseRedirect(reverse('images:view_imageset', args=(imageset.id,)))


@login_required
def delete_imageset(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.user.has_perm('delete_set', imageset):
        shutil.rmtree(imageset.root_path())
        imageset.delete()
    return HttpResponseRedirect(reverse('users:team', args=(imageset.team.id,)))


def dl_script(request):
    return TemplateResponse(
        request, 'images/download.sh', content_type='text/plain')
