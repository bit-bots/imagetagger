#!/usr/bin/env python3

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

BaseUrl = "{{ base_url }}" + "/"
if len(sys.argv) < 2:
    imageset = input("Imagesets you want to download, separated by a ',' or ' ':")
else:
    if sys.argv[1] == '-h':
        print("This script will download images from the specified imageset for you.")
        print("The images will be downloaded from: {}".format(BaseUrl))
        print("If errors occur during the download you will be notified at the end of the script execution")
        print("Just execute it with ./imagetagger_dl_script.py")
        sys.exit()
    else:
        imageset = " ".join(sys.argv[1:])

user = input("Username: ")
password = getpass.getpass()
print()
print("Enter in which directory your images should be saved relative to your current directory")
filename = input("The Imagesets will be stored in a subdirectory named after their id (default is current directory): ")
if filename.startswith('./'):
    filename = filename[2:]
if not os.path.exists(os.getcwd() + '/' + filename):
    os.makedirs(os.getcwd() + '/' + filename)
imagesets = set(imageset.replace(',', ' ').split(" "))
errorlist = list()
error = False
for userint in imagesets:
    if not userint.isdigit():
        print("{} is not a valid integer, please use integer for the imagesets".format(userint))
        error = True
if error:
    sys.exit()

error = False

loginpage = requests.get(BaseUrl)

cookies = {'csrftoken': loginpage.cookies['csrftoken']}
data = {'username': user,
        'password': password,
        'csrfmiddlewaretoken': loginpage.cookies['csrftoken']}
loggedinpage = requests.post(
    '{}user/login/'.format(BaseUrl),
    data=data,
    cookies=cookies,
    allow_redirects=False,
    headers={'referer': BaseUrl})

try:
    sessionid = loggedinpage.cookies['sessionid']
except KeyError:
    print('Login failed')
    sys.exit(1)
cookies = {'sessionid': sessionid}


def download_zip(current_imageset):
    if not os.path.exists(os.path.join(os.getcwd(), filename, current_imageset)):
        os.makedirs(os.path.join(os.getcwd(), filename, current_imageset))
    ziplink = f"{BaseUrl}images/imageset/{current_imageset}/download/"
    with requests.get(ziplink,
                     data=data,
                     cookies=cookies,
                     allow_redirects=False,
                     headers={'referer': BaseUrl},
                     stream=True) as r:
        filepath = os.path.join(filename, current_imageset)
        full_zipname = os.path.join(filepath, current_imageset+".zip")
        with open(full_zipname, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        with zipfile.ZipFile(full_zipname, 'r') as unzip:
            unzip.extractall(filepath)
        os.remove(full_zipname)
    print(f"Downloaded imageset {current_imageset}")

# Download images individually. This is slower than downloading the zip, so the zip is used by default.
def download_imageset(current_imageset):
    page = requests.get("{}images/imagelist/{}/".format(BaseUrl,
                        current_imageset),
                        cookies=cookies)
    if page.status_code == 404:
        print("In Imageset {} was an error. The server returned page not found.".format(current_imageset))
        errorlist.append(current_imageset)
        return
    images = page.text.replace('\n', '')
    images = images.split(',')
    for index, image in enumerate(images):
        if image == '':
            continue
        r = requests.get(BaseUrl + image[1:],
                         data=data,
                         cookies=cookies,
                         allow_redirects=False,
                         headers={'referer': BaseUrl},
                         stream=True)
        if r.status_code == 404:
            print("In Imageset {} was an error. The server returned page not found.".format(current_imageset))
            errorlist.append(current_imageset)

            error = True
            continue
        image = image.split('?')[1]
        with open(os.path.join(filename, current_imageset, image), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            sys.stdout.flush()
            print("{}Image {} / {} has been downloaded from imageset {}".format("\r", index + 1, len(images) - 1, current_imageset), end="")
    if not error:
        print('\nImageset {} has been downloaded.'.format(current_imageset))


for imgset in imagesets:
    if imgset is not " ":
        download_zip(imgset)
if errorlist:
    print("There have been errors while downloading the following imagesets: ")
    for item in errorlist:
        print(item)
