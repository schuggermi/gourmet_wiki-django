#!/bin/sh
set -e

echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
wait-for-it.sh -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -t 30 -- echo "PostgreSQL started"

npm run build

python manage.py makemigrations --settings=gourmet_wiki.settings
python manage.py migrate --settings=gourmet_wiki.settings
python manage.py collectstatic --settings=gourmet_wiki.settings --no-input --clear

exec "$@"
