# Installation

1. install required python packages.

```
pip3 install -r requirements.txt
```

2. install postgresql

```
# for Ubuntu
sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib
```

3. create database and user

```
sudo su - postgres psql
CREATE DATABASE imagetagger;
CREATE USER imagetagger WITH PASSWORD 'imagetagger';
```

4. migrate

```
python3 imagetagger/manage.py migrate
```

5. runserver
```
python3 imagetagger/manage.py runserver
```
