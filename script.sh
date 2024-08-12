#! /bin/bash

sleep 10
python3 manage.py makemigrations
python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn django_rest_api.wsgi:application --bind 0.0.0.0:8000