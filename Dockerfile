############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# use python 3 as base image
FROM python:3

# some environment variables
ENV PYTHONUNBUFFERED 1
ENV TAGGER_SRC imagetagger
ENV TAGGER_SRVHOME /srv
ENV TAGGER_SRVPROJ /srv/imagetagger
ENV TAGGER_SRVPKG /srv/imagetagger/imagetagger

# copy source code
RUN mkdir $TAGGER_SRVHOME
WORKDIR $TAGGER_SRVHOME
COPY $TAGGER_SRC $TAGGER_SRVHOME

# install python dependences
RUN pip3 install -r $TAGGER_SRVPROJ/requirements.txt

# install postgresql
RUN apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib

# port to expose
EXPOSE 8080

# check database is avaliable and then run migration
ENTRYPOINT ["$TAGGER_SRVPROJ/docker-entrypoint.sh"]

# Start ImageTagger
CMD ["python3", "imagetagger/manage.py", "runserver"]
