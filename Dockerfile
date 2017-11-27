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

# copy source code
ADD . /imagetagger/

RUN pip3 install --no-cache-dir -r /imagetagger/requirements.txt

ENTRYPOINT ["/imagetagger/docker-entrypoint.sh"]
