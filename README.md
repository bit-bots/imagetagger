# ImageTagger

This is a collaborative online tool for labeling image data.

If you are participating in RoboCup, you should not install your own instance but rather use the one provided by the Hamburg Bit-Bots (https://imagetagger.bit-bots.de). This enables you to use already labeled images from other teams and to share your own.

For a short overview of the functions please have a look at the following poster: https://robocup.informatik.uni-hamburg.de/wp-content/uploads/2017/11/imagetagger-poster.pdf

## Features

* team creation
* image sets
* bounding box, polygon, line and point labeling
* imageset download
* export format creation
* label export
* image preloading for labeling and verification
* label verification
* upload of existing labels
* tools exchange


## Planned Features

* collections of filtered images from multiple imagesets
* image metadata (e.g. robot pose, camera parameters)

## Reference

This paper describes the Bit-Bots Imagetagger more in depth. Please cite if you use this tool in your research:

FIEDLER, Niklas, et al. [ImageTagger: An Open Source Online Platform for Collaborative Image Labeling.](https://robocup.informatik.uni-hamburg.de/wp-content/uploads/2018/11/imagetagger_paper.pdf) In: RoboCup 2018: Robot World Cup XXII. Springer, 2018.

```
@inproceedings{imagetagger2018,
   author={Fiedler, Niklas and Bestmann, Marc and Hendrich, Norman},
   year={2018},
   title={ImageTagger: An Open Source Online Platform for Collaborative Image Labeling},
   booktitle={RoboCup 2018: Robot World Cup XXII},
   organization={Springer}
}
```
## Upgrade

```
pip install -U -r requirements.txt
./manage.py migrate
```

for additional steps on some releases see instructions
in [UPGRADE.md](https://github.com/bit-bots/imagetagger/blob/master/UPGRADE.md)

## Install

Checkout the latest release:

```
git checkout v0.x
```

In our production Senty is used for error reporting (pip install raven).
django-auth-ldap is used for login via ldap
uwsgi is used to serve the app to nginx

Install Python Dependencies:

```
pip3 install -r requirements.txt
```

Copy settings.py.example to settings.py in the imagetagger folder:

```
cp imagetagger/settings.py.example imagetagger/settings.py
```

and customize the settings.py.

The following settings should probably be changed:

+ The secret key
+ The DEBUG setting
+ The ALLOWED\_HOSTS
+ The database settings
+ The UPLOAD\_FS\_GROUP to the id of the group that should access and create the uploaded images

For the database, postgresql is used. Install it by running `sudo apt install postgresql`

Initialize the database cluster with `sudo -iu postgres initdb --locale en_US.UTF-8 -D '/var/lib/postgres/data'`

To start the postgresql server, run `sudo systemctl start postgresql.service`. If the server should always be started on boot, run `sudo systemctl enable postgresql.service`.

Then, create the user and the database by running

`sudo -iu postgres psql`

and then, in the postgres environment

```
CREATE USER imagetagger PASSWORD 'imagetagger';
CREATE DATABASE imagetagger WITH OWNER imagetagger ENCODING UTF8;
```

where of course the password and the user should be adapted to the ones specified in the database settings in the settings.py.

To initialize the database, run `./manage.py migrate`

To create an administrator user, run `./manage.py createsuperuser`.

`./manage.py runserver` starts the server with the configuration given in the settings.py file.

To create annotation types, log into the application and click on Administration at the very bottom of the home page.

For **production** systems it is necessary to run the following commands after each upgrade

```bash
./manage.py migrate
./manage.py compilemessages
./manage.py collectstatic
```

Our production uwisgi config can be found at https://github.com/fsinfuhh/mafiasi-rkt/blob/master/imagetagger/uwsgi-imagetagger.ini

Example Nginx Config:

```
server {
        listen 443;
        server_name imagetagger.bit-bots.de;

        ssl_certificate /etc/letsencrypt/certs/imagetagger.bit-bots.de/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/certs/imagetagger.bit-bots.de/privkey.pem;
        include /etc/nginx/ssl.conf;
        include /etc/nginx/acme.conf;
        ssl on;

        client_max_body_size 4G;

        access_log /var/log/nginx/imagetagger.bit-bots.de.access.log;
        error_log /var/log/nginx/imagetagger.bit-bots.de.error.log;

        location /static {
                expires 1h;
                alias /var/www/imagetagger;
        }

        location /ngx_static_dn/ {
                internal;
                alias /srv/data/imagetagger/storage/pictures/;
        }

        location / {
                include uwsgi_params;
                uwsgi_pass 127.0.0.1:4819;
                uwsgi_read_timeout 120;
        }
}
```

If you want to provide zip files of image sets, set `ENABLE_ZIP_DOWNLOAD = True` in your `settings.py`.
A daemon that creates and updates the zip files is necessary, you can start it with `./manage.py runzipdaemon`.
Please take into account that the presence of zip files will double your storage requirement.

Zip archive download via a script is also possible. The URL is `/images/imageset/<id>/download/`. A successful request
returns HTTP 200 OK and the zip file. When the file generation is still in progress, HTTP 202 ACCEPTED is returned.
For an empty image set, HTTP 204 NO CONTENT is returned instead of an empty zip archive.

## Used dependencies

The ImageTagger relies on the following plugins, libraries and frameworks:

- [Bootstrap](https://getbootstrap.com/)
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](http://www.django-rest-framework.org/)
- [django-registration](https://github.com/ubernostrum/django-registration)
- [django-widget-tweaks](https://github.com/jazzband/django-widget-tweaks)
- [imgAreaSelect](http://odyniec.net/projects/imgareaselect/)
- [jCanvas](https://projects.calebevans.me/jcanvas/)
- [jQuery](https://jquery.com/)
- [jQuery-Autocomplete](https://github.com/devbridge/jquery-Autocomplete)
- [jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload)
- [Pillow](https://github.com/python-pillow/Pillow)
- [PostgreSQL](https://www.postgresql.org/)

We are grateful to the maintainers and contributors of the respective projects.
