FROM docker.io/debian:buster-slim

# install imagetagger system dependencies
RUN apt-get update && \
	apt-get install --no-install-recommends -y g++ wget uwsgi-plugin-python3 python3 python3-pip node-uglify make git \
	    python3-psycopg2 python3-ldap3 python3-pkg-resources gettext gcc python3-dev python3-setuptools libldap2-dev \
	    libsasl2-dev nginx

# add requirements file
WORKDIR /app/src
COPY imagetagger/requirements.txt /app/src/requirements.txt

# install python dependencies
RUN pip3 install -r /app/src/requirements.txt
RUN	pip3 install sentry-sdk uwsgi django-ldapdb django-auth-ldap

# clean container
RUN apt-get purge -y --auto-remove node-uglify git python3-pip make gcc python3-dev libldap2-dev libsasl2-dev \
    python3-setuptools
RUN apt-get clean

# add remaining sources
COPY imagetagger /app/src/imagetagger

# configure /app/config/imagetagger_settings to be python importable so that one can use their own settings file
RUN mkdir -p /app/data /app/static /app/config/imagetagger_settings
RUN touch /app/config/imagetagger_settings/__init__.py
ENV PYTHONPATH=$PYTHONPATH:/app/config:/app/src/imagetagger

# configure runtime environment
RUN sed -i 's/env python/env python3/g' /app/src/imagetagger/manage.py

ARG UID_WWW_DATA=5008
ARG GID_WWW_DATA=33
RUN usermod -u $UID_WWW_DATA -g $GID_WWW_DATA -d /app/data/ www-data
RUN chown -R www-data /app

RUN /app/src/imagetagger/manage.py collectstatic --no-input

COPY docker/uwsgi_imagetagger.ini /etc/uwsgi/imagetagger.ini
COPY docker/nginx.conf /etc/nginx/sites-enabled/default
COPY docker/update_points docker/zip_daemon docker/run /app/bin/
RUN ln -sf /app/bin/* /usr/local/bin
ENTRYPOINT ["/usr/local/bin/run"]
ENV IN_DOCKER=true
ENV DJANGO_CONFIGURATION=Prod

# add image metadata
EXPOSE 3008
EXPOSE 80
VOLUME /app/config
VOLUME /app/data

