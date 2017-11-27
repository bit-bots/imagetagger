#!/bin/sh
set -e

# until psql $DATABASE_URL -c '\l'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done

# >&2 echo "Postgres is up - continuing"

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    python3 /imagetagger/imagetagger/manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
    python3 /imagetagger/imagetagger/manage.py collectstatic --noinput
fi

exec "$@"
