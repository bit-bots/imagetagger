#!/bin/sh
set -e

# until psql $DATABASE_URL -c '\l'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done

# >&2 echo "Postgres is up - continuing"

if [ "x$DJANGO_INIT" = 'xon' ]; then
    cp /imagetagger/imagetagger/settings.py.docker /imagetagger/imagetagger/settings.py
    python /imagetagger/imagetagger/manage.py migrate --noinput
fi

exec "$@"
