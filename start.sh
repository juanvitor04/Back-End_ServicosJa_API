#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Checking DATABASE_URL..."
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL is not set. Using default (SQLite)."
else
    echo "DATABASE_URL is set."
fi

echo "Running migrations..."
python manage.py migrate --noinput --verbosity 2

echo "Creating superuser..."
python create_superuser.py

echo "Creating initial services..."
python manage.py shell < criar_services.py

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000

