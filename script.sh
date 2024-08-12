#! /bin/bash

sleep 10
python3 manage.py makemigrations
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py test
