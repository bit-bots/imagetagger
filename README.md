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

## Installing and running Imagetagger
Imagetagger can be installed and run locally (best for development), in a docker container or in Kubernetes 
(used in our deployment).

### Locally

1.  #### Install the latest release
    
    You should probably do this in a [virtual environment](https://virtualenv.pypa.io/en/stable/) 
    ```shell
    git checkout v…
    pip3 install -r imagetagger/requirements.txt
    ```
   
2.  #### Setup a database server
    
    As a database server [postgresql](https://www.postgresql.org/) is required.
    Please seek a guide specific to your operating system on how to install a server and get it running.
   
    Once postgresql is installed, a user and database need to be set up for imagetagger.
    Of course, the user and password can be changed to something else.
    ```postgresql
    CREATE USER imagetagger PASSWORD 'imagetagger';
    CREATE DATABASE imagetagger WITH OWNER imagetagger;
    ```

3.  #### Configuring ImageTagger to connect to the database
    
    Please see the lower section about application configuration on how to configure ImageTagger for your specific
    database credentials.
   
4.  #### Initialize the database
    
    Run the following to create and setup all necessary database tables:
    ```shell
    ./manage.py migrate
    ```

5.  #### Create a user
    
    ```shell
    export DJANGO_CONFIGURATION=Prod
    ./manage.py createsuperuser
    ```

6.  #### Run the server
    
    ```shell
    export DJANGO_CONFIGURATION=Prod
    ./manage.py runserver
    ```
   
**In a production deployment** it is necessary to run the following commands after each upgrade:
```shell
export DJANGO_CONFIGURATION=Prod
./manage.py migrate
./manage.py compilemessages
./manage.py collectstatic
```

for additional steps on some releases see instructions in [UPGRADE.md](https://github.com/bit-bots/imagetagger/blob/master/UPGRADE.md)

### In-Docker

1.  #### Checkout the latest release
    
    ```shell
    git checkout v…
    ```

2.  #### Build the container image
    
    *Note:* the Dockerfile has been tested with [podman](https://podman.io/) as well.
    ```shell
    docker build -t imagetagger .
    ```
   
3.  #### Run the container
    
    ```shell
    docker run -it -p 8000:80 --name imagetagger imagetagger
    ```
   
    This step will not work out of the box because configuration still needs to be done.
    See the lower section about configuring ImageTagger on how to fix this.

4.  #### Create a user
    
    *Note: This step requires a container running in the background.*
    ```shell
    docker exec imagetagger /app/src/imagetagger/manage.py createsuperuser
    ```
   
#### About the Container 

| Kind | Description |
|---|---|
| Volume | `/app/data` is where persistent data (like images) are stored
| Environment | ImageTagger can mostly be configured via environment variables
| Ports | The container internal webserver listens on port 80 for incoming connections.

### On Kubernetes

1.  Follow the steps for *In-Docker* on how to build a container image

2.  **Apply kubernetes configuration**

    *Note: This assumes you have access to a kubernetes cluster configured and can use kubectl*
    
    We use [kustomize](https://kustomize.io/) for management of our kubernetes configuration.
    It can be applied by running the following commands:
    ```shell
    kustomize build . > k8s.yml
    kubectl apply -f k8s.yml
    ```
   
#### Generated Kubernetes resources

| Kind | Name | Description
|---|---|---
| [Namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) | imagetagger | The namespace in which each resource resides
| [Deployment](https://kubernetes.io/es/docs/concepts/workloads/controllers/deployment/) + [Service](https://kubernetes.io/docs/concepts/services-networking/service/) | imagetagger-postgres | postgresql server which is required by ImageTagger. The replica count can be dialed down to 0 if an the usage of an external server is desired.
| [PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) | imagetagger-database | Where the postgresql server stores its data
| [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) | imagetagger-postgres | Configuration of the postgresql server. Also available inside the application server deployment so that settings can be [referenced](https://kubernetes.io/docs/tasks/inject-data-application/define-interdependent-environment-variables/).
| [Deployment](https://kubernetes.io/es/docs/concepts/workloads/controllers/deployment/) + [Service](https://kubernetes.io/docs/concepts/services-networking/service/) | imagetagger-web | application server. Per default this deployment references the image `imagetagger:local` which is probably not resolvable and should be replaced by a reference to where your previously built container image is available.
| [PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) | imagetagger-image-data | Where the application server stores its images (and tools).
| [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) | imagetagger-web | Configuration of the application server. Mounted as environment variables.

## Configuration

ImageTagger is a Django application and uses [django-configurations](https://django-configurations.readthedocs.io/en/stable/)
for better configuration management.

It is configured to use a *Dev* configuration when running locally and *Prod* when running in a container.
This can be overridden via the environment variable `DJANGO_CONFIGURATION`.

For a list of available configuration values see [settings.py](https://github.com/bit-bots/imagetagger/blob/master/imagetagger/imagetagger/settings.py). 
Towards the bottom is a list of *values*. These are taken from environment variables where the key is the variable name
but with an `IT_` prefix.

If completely custom configuration is desired, `imagetagger/imagetagger/settings_local.py` can be created in which
a custom configuration class may be created. In docker this file may be located at `/app/config/settings.py` so that
mounting it should be simple.
To use this custom configuration class, the environment variables `DJANGO_SETTINGS_MODULE=imagetagger.settings_local`
and `DJANGO_CONFIGURATION=MyCustomClass` must be set.

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
