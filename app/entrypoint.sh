#!/bin/sh

wait-for-it.sh "$POSTGRES_HOST":"$POSTGRES_PORT" -- echo "PostgreSQL started"

python ./manage.py makemigrations --settings=gourmet_wiki.settings
python ./manage.py migrate --settings=gourmet_wiki.settings
python ./manage.py collectstatic --settings=gourmet_wiki.settings --no-input --clear

exec "$@"