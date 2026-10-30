#!/bin/sh
set -e

if [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

if [ "$SEED_DATA" = "1" ] && [ -n "$SEED_COMMAND" ]; then
    echo "Seeding data ($SEED_COMMAND)..."
    python manage.py "$SEED_COMMAND"
fi

exec "$@"