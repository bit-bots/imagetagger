import hashlib
import imghdr
import os
import random
import shutil
import string
import zipfile

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from PIL import Image as PIL_Image

from imagetagger.images.models import ImageSet, Image


def handle_upload(imageset_id, files, user):
    """
    Handle the upload of new image files to an Imageset.

    :param imageset_id: ID of the Imageset to which the new files will get added
    :param files: Array of files which are getting uploaded. Typically retrieved from request.FILES
    :param user: The user who is uploading. Typically retrieved from request.user
    :rtype: django.http.HttpResponse
    """

    imageset = get_object_or_404(ImageSet, id=imageset_id)
    if imageset.has_perm('edit_set', user) and not imageset.image_lock:
        if files is None:
            return HttpResponseBadRequest('Must have files attached!')
        json_files = []
        for f in files.getlist('files[]'):
            error = {
                'duplicates': 0,
                'damaged': False,
                'directories': False,
                'exists': False,
                'unsupported': False,
                'zip': False,
            }
            magic_number = f.read(4)
            f.seek(0)  # reset file cursor to the beginning of the file
            if magic_number == b'PK\x03\x04':  # ZIP file magic number
                error['zip'] = True
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
                    file_path = os.path.join(imageset.root_path(), 'tmp', filename)
                    try:
                        if imghdr.what(file_path) in settings.IMAGE_EXTENSION:
                            # creates a checksum for image
                            fchecksum = hashlib.sha512()
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
                                (shortname, extension) = os.path.splitext(filename)
                                img_fname = (''.join(shortname) + '_' +
                                             ''.join(
                                                 random.choice(
                                                     string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                                 for _ in range(6)) + extension)
                                try:
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
                                except (OSError, IOError):
                                    error['damaged'] = True
                                    os.remove(file_path)
                            else:
                                os.remove(file_path)
                                duplicat_count = duplicat_count + 1
                        else:
                            error['unsupported'] = True
                    except IsADirectoryError:
                        error['directories'] = True
                if duplicat_count > 0:
                    error['duplicates'] = duplicat_count
            else:
                # creates a checksum for image
                fchecksum = hashlib.sha512()
                for chunk in f.chunks():
                    fchecksum.update(chunk)
                fchecksum = fchecksum.digest()
                # tests for duplicats in  imageset
                if Image.objects.filter(checksum=fchecksum, image_set=imageset) \
                        .count() == 0:
                    fname = f.name.split('.')
                    fname = ('_'.join(fname[:-1]) + '_' +
                             ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                     for _ in range(6)) + '.' + fname[-1])
                    image = Image(
                        name=f.name,
                        image_set=imageset,
                        filename=fname,
                        checksum=fchecksum)
                    os.makedirs(os.path.dirname(image.path()))
                    with open(image.path(), 'wb') as out:
                        for chunk in f.chunks():
                            out.write(chunk)
                    shutil.chown(image.path(), group=settings.UPLOAD_FS_GROUP)
                    if imghdr.what(image.path()) in settings.IMAGE_EXTENSION:
                        try:
                            with PIL_Image.open(image.path()) as image_file:
                                width, height = image_file.size
                            image.height = height
                            image.width = width
                            image.save()
                        except (OSError, IOError):
                            error['damaged'] = True
                            os.remove(image.path())
                    else:
                        error['unsupported'] = True
                        os.remove(image.path())
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
                json_files.append({'name': f.name,
                                   'size': f.size,
                                   # 'url': reverse('images_imageview', args=(image.id, )),
                                   # 'thumbnailUrl': reverse('images_imageview', args=(image.id, )),
                                   # 'deleteUrl': reverse('images_imagedeleteview', args=(image.id, )),
                                   # 'deleteType': "DELETE",
                                   })
            else:
                json_files.append({'name': f.name,
                                   'size': f.size,
                                   'error': errormessage,
                                   })

        return JsonResponse({'files': json_files})


def handle_delete():
    pass
