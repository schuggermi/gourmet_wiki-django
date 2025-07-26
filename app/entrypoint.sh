#!/bin/sh

if [ "$DATABASE" = "$POSTGRES_DB" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python ./manage.py makemigrations --settings=gourmet_wiki.settings
python ./manage.py migrate --settings=gourmet_wiki.settings
python ./manage.py collectstatic --settings=gourmet_wiki.settings --no-input --clear

exec "$@"