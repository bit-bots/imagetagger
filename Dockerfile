############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# use python 3 as base image
FROM python:3

# some environment variables
ENV PYTHONUNBUFFERED 1

# create work directory
RUN mkdir -p /imagetagger
WORKDIR /imagetagger

# install python dependences
ADD requirements.txt /imagetagger/
RUN pip3 install --no-cache-dir -r requirements.txt

# copy source code
ADD . /imagetagger/
