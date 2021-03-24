#!/usr/bin/env python3

import argparse
import sys
import getpass
import shutil
import os
import zipfile

try:
    import requests
except ImportError:
    print("Python3 requests is not installed. Please use e.g. pip3 install requests")
    sys.exit()

BASE_URL = "{{ base_url }}/"


def login(user, password):
    """Log into the imagetagger. Returns POST data and cookies"""
    login_page = requests.get(BASE_URL)

    cookies = {'csrftoken': login_page.cookies['csrftoken']}
    data = {'username': user,
            'password': password,
            'csrfmiddlewaretoken': login_page.cookies['csrftoken']}
    logged_in_page = requests.post(
        f'{BASE_URL}user/login/',
        data=data,
        cookies=cookies,
        allow_redirects=False,
        headers={'referer': BASE_URL})

    cookies = login_page.cookies
    try:
        cookies['sessionid'] = logged_in_page.cookies['sessionid']
    except KeyError:
        return False
    return data, cookies


def download_zip(set_id, target_folder, login_data):
    """
    Downloads an imageset as zip file

    :param set_id: The id of the image set to download
    :param target_folder: The folder in which the images should be saved
    :param login_data: Data as returned by login()
    """
    print(f"Now downloading {set_id}")

    os.makedirs(target_folder, exist_ok=True)

    zip_link = f"{BASE_URL}images/imageset/{set_id}/download/"

    with requests.get(zip_link,
                      data=login_data[0],
                      cookies=login_data[1],
                      allow_redirects=False,
                      headers={'referer': BASE_URL},
                      stream=True) as r:
        # this is intended for the case when an imageset does not exist or the zip does not yet exist
        if r.status_code == 404:
            print(f"In Imageset {set_id} was an error. The server returned page not found."
                  "Try --separate if zip download is disabled.")
            return False

        full_zipname = os.path.join(target_folder, f"{set_id}.zip")
        with open(full_zipname, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        with zipfile.ZipFile(full_zipname, 'r') as unzip:
            unzip.extractall(target_folder)
        os.remove(full_zipname)

    print(f"Downloaded imageset {set_id}")
    return True


def download_imageset(set_id, target_folder, login_data):
    """
    Downloads an imageset as separate files

    :param set_id: The id of the image set to download
    :param target_folder: The folder in which the images should be saved
    :param login_data: Data as returned by login()
    """
    print(f'Now downloading {set_id}')

    os.makedirs(target_folder, exist_ok=True)

    page = requests.get(f"{BASE_URL}images/imagelist/{set_id}/", cookies=login_data[1])
    if page.status_code == 404:
        print("In Imageset {} was an error. The server returned page not found.".format(set_id))
        return False

    images = page.text.replace('\n', '')
    images = images.split(',')
    error = True

    for index, image in enumerate(images):
        if image == '':
            continue
        r = requests.get(BASE_URL + image[1:],
                         data=login_data[0],
                         cookies=login_data[1],
                         allow_redirects=False,
                         headers={'referer': BASE_URL},
                         stream=True)
        if r.status_code == 404:
            print("In Imageset {} was an error. The server returned page not found.".format(set_id))
            error = True
            continue

        image = image.split('?')[1]
        with open(os.path.join(target_folder, image), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            sys.stdout.flush()
            print(f"\rImage {index + 1} / {len(images) - 1} has been downloaded from imageset {set_id}", end="")

    print()

    if not error:
        print('\nImageset {} has been downloaded.'.format(set_id))
    return error


def download_annotations(set_id, export_id, target_folder, login_data):
    """
    Downloads annotations for an imageset

    :param set_id: The id of the image set for which the annotations will be saved
    :param export_id: The id of the export format
    :param target_folder: The folder in which the images should be saved
    :param login_data: Data as returned by login()
    """
    export_format_data = login_data[0]
    export_format_data['imageset_id'] = set_id
    export_format_data['export_format_id'] = export_id

    response = requests.post(BASE_URL + "annotations/api/export/create/", data=export_format_data,
                             cookies=login_data[1], headers={'referer': BASE_URL})
    if response.status_code == 403:
        print(f'You cannot create exports for dataset {set_id}.')
        return False

    response = response.json()
    export_url = BASE_URL + f"/annotations/export/{response['export_id']}/download/"
    r = requests.get(export_url,
                     data=login_data[0],
                     cookies=login_data[1],
                     allow_redirects=False,
                     headers={'referer': BASE_URL},
                     stream=True)

    export_name = os.path.join(target_folder, str(set_id) + ".txt")
    with open(export_name, "wb") as f:
        f.write(r.content)
    print(f'Downloaded annotations for imageset {set_id}')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script will download images from the specified imageset for you.'
                                                 f' The images will be downloaded from: {BASE_URL}')
    parser.add_argument('-s', '--separate', action='store_true', default=False,
                        help='Download the images separately instead of bundled in a ZIP file')
    parser.add_argument('-a', '--annotations', action='store_true', default=False,
                        help='Also download annotations')
    parser.add_argument('-e', '--export-format', type=int,
                        help='Export format to use in the annotation download. '
                             f'Please visit {BASE_URL}/annotations/api/export_format/list/ while logged in '
                             'to find the id of your export format')
    parser.add_argument('-u', '--username', type=str, help='ImageTagger username')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(),
                        help='Folder where imagesets will be stored in subdirectories'
                             'named after their id. Default is the current directory')
    parser.add_argument('imagesets', nargs='+', type=int, metavar='SET_ID',
                        help='A list of imagesets to download')
    args = parser.parse_args()

    if not args.username:
        args.username = input("Username: ")

    password = getpass.getpass()

    if args.annotations and not args.export_format:
        print(f'Please visit {BASE_URL}/annotations/api/export_format/list/ '
              'while logged in to find the id of your export format')
        format_id = input("Enter your export format id: ")
        if not format_id.isdigit():
            sys.exit(f'{format_id} is not a valid integer.')
        args.export_format = format_id

    folder = os.path.join(os.path.realpath(args.directory))
    os.makedirs(folder, exist_ok=True)

    login_data = login(args.username, password)
    if not login_data:
        sys.exit('Login failed')

    error_list = []
    for imgset in args.imagesets:
        set_folder = os.path.join(folder, str(imgset))
        if not args.separate:
            if not download_zip(imgset, set_folder, login_data):
                error_list.append(imgset)
        else:
            if not download_imageset(imgset, set_folder, login_data):
                error_list.append(imgset)

        if args.annotations:
            if not download_annotations(imgset, args.export_format, set_folder, login_data):
                error_list.append(imgset)

    if error_list:
        print("There have been errors while downloading the following imagesets: ")
        print(', '.join(str(error) for error in error_list))
