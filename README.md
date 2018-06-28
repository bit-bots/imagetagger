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

FIEDLER, Niklas, et al. ImageTagger: An Open Source Online Platform for Collaborative Image Labeling. In: RoboCup 2018: Robot World Cup XXII. Springer, 2018.

```
@inproceedings{imagetagger2018,
   author={Fiedler, Niklas and Bestmann, Marc and Hendrich, Norman},
   year={2018},
   title={ImageTagger: An Open Source Online Platform for Collaborative Image Labeling},
   booktitle={RoboCup 2018: Robot World Cup XXII}
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
pip install -r requirements.txt
```

Copy settings.py.example to settings.py in the imagetagger folder:

```
cp imagetagger/settings.py.example imagetagger/settings.py
```

and customize the settings.py.

For Production systems it is necessary to run the following commands after each upgrade

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
