from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth import logout, login
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from .models import ImageSet, Image, AnnotationType, Annotation, Export, Verification, Team
from django.conf import settings
from django.db.models import Q
from django.core.files.uploadedfile import UploadedFile
import os
import shutil
import string
import random
import json
from datetime import datetime
from guardian.shortcuts import assign_perm
import zipfile

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
    userteams = Team.objects.filter(members__in=request.user.groups.all())
    imagesets = ImageSet.objects.filter(team__in=userteams).order_by('id')
    return TemplateResponse(request, 'images/index.html', {
                            'image_sets': imagesets,
                            'userteams': userteams,
                            })


@login_required
@require_http_methods(["POST", ])
def imageuploadview(request, imageset_id):
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
                        img_fname = ''.join(shortname) + '_' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) + extension
                        shutil.move(os.path.join(imageset.root_path(), 'tmp', filename), os.path.join(imageset.root_path(), img_fname))
                        Image(name=filename, image_set=imageset, filename=img_fname).save()
            else:
                fname = '_'.join(fname[:-1]) + '_' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) + '.' + fname[-1]
                image = Image(name=f.name, image_set=imageset, filename=fname)
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


@login_required
def imageview(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    with open(os.path.join(settings.STATIC_ROOT, image.path()), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")


def image_auth_nginx(request, image_id):
    """
    This view is to authenticate direct access to the images via nginx auth_request directive

    it will return forbidden on if the user is not authenticated
    """
    if request.user.is_anonymous:
        return HttpResponseForbidden()
    image = get_object_or_404(Image, id=image_id)
    if not request.user.has_perm('read', image.image_set_id):
        return HttpResponseForbidden()

    return HttpResponse()


@login_required
def get_image_list(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if not request.user.has_perm('read', imageset):
        return HttpResponseForbidden()
    return TemplateResponse(request, '', {
        'images': imageset.image_set
    })
        


@login_required
@csrf_exempt
@require_http_methods(["DELETE", ])
def imagedeleteview(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.user.has_perm('edit_imageset', image.image_set):
        os.remove(os.path.join(settings.STATIC_ROOT, image.full_path()))
        image.delete()
        return JsonResponse({'files': [{image.name: True}, ]})


@login_required
def imagesetview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    # images the imageset contains
    images = Image.objects.filter(image_set=imageset).order_by('id')
    # the saved exports of the imageset
    exports = Export.objects.filter(image_set=image_set_id).order_by('-id')[:5]
    # a list of annotation types used in the imageset
    annotation_types = set()
    annotations = set()
    for image in images:
        annotations = annotations.union(Annotation.objects.filter(image=image))
    annotation_types = annotation_types.union([annotation.type for annotation in annotations])
    first_annotation = None
    if len(annotations) > 0:
        first_annotation = annotations.pop()
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
def imagesetcreateview(request, team_id):
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
        os.mkdir(imageset.root_path())  # create a folder to store the images of the set
        assign_perm('edit_set', team.members, imageset)
        assign_perm('delete_set', team.admins, imageset)
        assign_perm('edit_annotation', team.members, imageset)
        assign_perm('delete_annotation', team.members, imageset)
        assign_perm('annotate', team.members, imageset)
        assign_perm('read', team.members, imageset)
        assign_perm('create_export', team.members, imageset)
        assign_perm('delete_export', team.members, imageset)
        return HttpResponseRedirect(reverse('images_imagesetview', args=(imageset.id,)))
    return HttpResponseRedirect(reverse('images_teamview', args=(team.id,)))


@login_required
@require_http_methods(["POST", ])
def imageseteditview(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.user.has_perm('edit_set', imageset):
        # todo: check if name and path are unique in the team
        imageset.name = request.POST["name"]
        imageset.location = request.POST["location"]
        imageset.description = request.POST["description"]
        imageset.public = "public" in request.POST
        imageset.image_lock = "image-lock" in request.POST
        imageset.save()
    return HttpResponseRedirect(reverse('images_imagesetview', args=(imageset.id,)))


@login_required
def imagesetdeleteview(request, imageset_id):
    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if request.user.has_perm('delete_set', imageset):
        shutil.rmtree(imageset.root_path())
        imageset.delete()
    return HttpResponseRedirect(reverse('images_teamview', args=(imageset.team.id,)))


@login_required
def tagview(request, image_id):
    selected_image = get_object_or_404(Image, id=image_id)
    if request.user.has_perm('annotate', selected_image.image_set) or selected_image.image_set.public:
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
        annotation_types = AnnotationType.objects.filter(active=True)  # needed to select the annotation in the drop-down-menu
        set_images = Image.objects.filter(image_set=selected_image.image_set)
        set_images = set_images.order_by('id')

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
    else:
        return HttpResponseRedirect(reverse('images_imagesetview', args=(selected_image.image_set.id,)))



@login_required
def tageditview(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.user is annotation.user or request.user.has_perm('edit_annotation', annotation.image.image_set):
        annotation_types = AnnotationType.objects.all()  # needed to select the annotation in the drop-down-menu
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
    else:
        return HttpResponseRedirect(reverse('images_tagview', args=(annotation.image.id,)))


@login_required
def tagdeleteview(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.user.has_perm('delete_annotation', annotation.image.image_set):
        annotation.delete()
        print('deleted annotation ', annotation_id)
    return HttpResponseRedirect(reverse('images_tagview', args=(annotation.image.id,)))


@login_required
def tageditsaveview(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.method == 'POST' \
            and verify_bounding_box_annotation(request.POST) \
            and (request.user is annotation.user
                 or request.user.has_perm('edit_annotation', annotation.image.image_set)):
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
    return HttpResponseRedirect(reverse('images_tagview', args=(annotation.image.id,)))


@login_required
def exportcreateview(request, image_set_id):
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    if request.user.has_perm('create_export', imageset) or imageset.public:
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
    return HttpResponseRedirect(reverse('images_imagesetview', args=(image_set_id,)))


#@login_required
#def exportdeleteview(request, export_id):
#    export = get_object_or_404(Export, id=export_id)
#    if request.user.has_perm('delete_export',
#        return HttpResponseRedirect(reverse('images_imagesetview', args=(export.image_set.id,)))


@login_required
def exportdownloadview(request, export_id):
    db_export = get_object_or_404(Export, id=export_id)
    export = db_export.export_text
    response = HttpResponse(export, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + export_id + '_export.txt"'
    return response


@login_required
def annotationmanageview(request, image_set_id):
    userteams = Team.objects.filter(members__in=request.user.groups.all())
    imagesets = ImageSet.objects.filter(team__in=userteams) | ImageSet.objects.filter(public=True)
    imageset = get_object_or_404(ImageSet, id=image_set_id)
    images = Image.objects.filter(image_set=imageset)
    annotations = Annotation.objects.filter(image__in=images)\
                                    .order_by('id')
    return TemplateResponse(request, 'images/annotationmanageview.html', {
                            'selected_image_set': imageset,
                            'image_sets': imagesets,
                            'annotations': annotations})

@login_required
def exploreview(request, mode):
    imagesets, teams, users = None, None, None
    if mode == 'team':
        teams = Team.objects.all()
        if request.method == 'POST':
            teams = teams.filter(name__contains=request.POST['searchquery'])
    elif mode == 'user':
        users = User.objects.all()
        if request.method == 'POST':
            users = users.filter(username__contains=request.POST['searchquery'])
    else:
        userteams = Team.objects.filter(members__in=request.user.groups.all())
        imagesets = ImageSet.objects.filter(team__in=userteams) | ImageSet.objects.filter(public=True)
        if request.method == 'POST':
            imagesets = imagesets.filter(name__contains=request.POST['searchquery'])

    return TemplateResponse(request, 'images/exploreview.html', {
                            'mode': mode,
                            'imagesets': imagesets,
                            'teams': teams,
                            'users': users, })

@login_required
def userview(request, user_id):
    user = get_object_or_404(User, id=user_id)
    userteams = Team.objects.filter(members__in=user.groups.all())

    # todo: count the points
    points = 0

    return TemplateResponse(request, 'images/userview.html', {
                            'user': user,
                            'userteams': userteams,
                            'userpoints': points, })

def createuserview(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return HttpResponseRedirect(reverse('images_userview', args=(user.id,)))


@login_required
def teamview(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST' and request.user.has_perm('user_management', team):
        user_to_add = User.objects.filter(username=request.POST['username'])[0]
        if user_to_add:
            team.members.user_set.add(user_to_add)

    members = team.members.user_set.all()
    is_member = request.user in members
    admins = team.admins.user_set.all()
    is_admin = request.user in admins  # The request.user is an admin of the team
    no_admin = len(admins) == 0  # Team has no admin, so every member can claim the Position
    imagesets = ImageSet.objects.filter(team=team)
    pub_imagesets = imagesets.filter(public=True).order_by('id')
    priv_imagesets = imagesets.filter(public=False).order_by('id')
    return TemplateResponse(request, 'images/teamview.html', {
                            'team': team,
                            'memberset': members,
                            'is_member': is_member,
                            'is_admin': is_admin,
                            'no_admin': no_admin,
                            'admins': admins,
                            'pub_imagesets': pub_imagesets,
                            'priv_imagesets': priv_imagesets, })


@login_required
def createteamview(request):
    name = request.POST['teamname']
    if len(name) <= 20 and len(name) >= 3:
        members = Group(name=name+'_members')
        members.save()
        admins = Group(name=name+'_admins')
        admins.save()
        user = request.user
        members.user_set.add(user)
        members.save()
        admins.user_set.add(user)
        admins.save()
        team = Team()
        team.name = name
        team.members = members
        team.admins = admins
        team.website = ''
        team.save()
        assign_perm('user_management', team.admins, team)
        assign_perm('create_set', team.members, team)
        return HttpResponseRedirect(reverse('images_teamview', args=(team.id,)))
    return HttpResponseRedirect(str('/images/'))


@login_required
def leaveteamview(request, team_id, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    team = get_object_or_404(Team, id=team_id)
    team.members.user_set.remove(user)
    team.admins.user_set.remove(user)
    return HttpResponseRedirect(reverse('images_teamview', args=(team.id,)))

@login_required
def enthroneview(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)
    if request.user.has_perm('user_management', team) or 0 == len(team.admins.user_set.all()):
        team.admins.user_set.add(user)
    return HttpResponseRedirect(reverse('images_teamview', args=(team.id,)))

@login_required
def dethroneview(request, team_id, user_id):
    user = get_object_or_404(User, id=user_id)
    team = get_object_or_404(Team, id=team_id)
    if request.user.has_perm('user_management', team):
        team.admins.user_set.remove(user)
    return HttpResponseRedirect(reverse('images_teamview', args=(team.id,)))

@login_required
def verifyview(request, annotation_id):
    # here the stuff we got via POST gets put in the DB
    if request.method == 'POST':  # TODO get shit working
        annotation = get_object_or_404(Annotation, id=request.POST['annotation'])
        if request.POST['state'] == 'accept':
            state = True
            user_verify(request.user, annotation, state)
        elif request.POST['state'] == 'reject':
            state = False
            user_verify(request.user, annotation, state)
    annotation = get_object_or_404(Annotation, id=annotation_id)
    image = get_object_or_404(Image, id=annotation.image.id)
    vector = json.loads(annotation.vector)
    set_images = Image.objects.filter(image_set=image.image_set)
    set_annotations = Annotation.objects.filter(image__in=set_images)
    set_annotations = set_annotations.order_by('id')  # good... hopefully
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
