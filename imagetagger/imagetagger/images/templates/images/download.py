import sys
import getpass
import requests
from bs4 import BeautifulSoup
import os
import shutil

# TODO: replace imagetagger.bit-bots.de with {{ base_url }}
# TODO: zielordner
# TODO: mehrere imagesets auf einmal
# TODO: -h
if len(sys.argv) < 2:
    imageset = input("Imageset:")
else:
    imageset = sys.argv[1]
print("Please enter Username and Password for the ImageTagger. This Script will download into the current directory.")
user = input("Username:")
password = getpass.getpass()


def download_imageset(current_imageset):
    #BaseUrl = "https://imagetagger.bit-bots.de/"#{{ base_url }}"
    BaseUrl = "http://127.0.0.1:8000/"
    loginpage = requests.get(BaseUrl)
    csrftoken = loginpage.cookies['csrftoken']
    loginsoup = BeautifulSoup(loginpage.text, 'html.parser')
    for i in loginsoup.find_all('input'):
        if i['name'] == 'csrfmiddlewaretoken':
            csrfmiddlewaretoken = i['value']
            break

    cookies = {'csrftoken': csrftoken}
    #cookies = {'csrfmiddlewaretoken': csrfmiddlewaretoken}
    data = {'username': user,
            'password': password,
            'csrfmiddlewaretoken': csrfmiddlewaretoken}
    loggedinpage = requests.post(
        '{}user/login/'.format(BaseUrl),
        data=data,
        cookies=cookies,
        allow_redirects=False,
        headers={'referer': BaseUrl})

    try:
        sessionid  = loggedinpage.cookies['sessionid']
    except:
        print('Login failed')
        sys.exit()
    print("Sessionid:"+sessionid)
    cookies = {'sessionid' : sessionid}
    page = requests.get("{}images/imagelist/{}/".format(BaseUrl, imageset),cookies = cookies)
    images = page.text.replace('\n','')
    images = images.split(',')
    for image in images:
        if image == '':
            continue
        r = requests.get(BaseUrl+image[1:],
                     data=data,
                     cookies=cookies,
                     allow_redirects=False,
                     headers={'referer': BaseUrl},
                     stream = True)
        print(image)
        print(BaseUrl+image[1:])
        image = image.split('?')[1]
        print(image)
        with open('tmp/{}'.format(image), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    print('Imageset {} has been downloaded.'.format(current_imageset))


download_imageset(imageset)