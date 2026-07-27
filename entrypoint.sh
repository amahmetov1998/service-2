#!/bin/sh

set -e

echo "Running migrations..."

alembic -c src/alembic.ini upgrade head

echo "Starting application..."

exec "$@"