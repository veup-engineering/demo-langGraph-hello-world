#!/bin/sh
set -e

# Run Django migrations if this is a Django service
if [ "$RUN_MIGRATIONS" = "true" ]; then
    python manage.py migrate --noinput
fi

exec "$@"
