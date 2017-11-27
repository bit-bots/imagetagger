############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# use python 3 as base image
FROM python:3.6.3-alpine

# some environment variables
ENV PYTHONUNBUFFERED 1

# create work directory
RUN mkdir -p /imagetagger
WORKDIR /imagetagger

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
ADD requirements.txt /imagetagger/
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
    && pyvenv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# copy source code
ADD . /imagetagger/

ENTRYPOINT ["/imagetagger/docker-entrypoint.sh"]
