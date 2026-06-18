#!/usr/bin/env sh
set -eu

python manage.py migrate --no-input
python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"
