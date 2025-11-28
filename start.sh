#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python create_superuser.py
gunicorn config.wsgi:application
