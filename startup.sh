#!/bin/bash

wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1H6zEriZ2GdwhE7rCwX-uJEOO7W8nwq0_22jb_-ntu48' -o GolfPoolSelections.csv
python manage.py migrate --noinput
python manage.py createsuperuser --noinput
gunicorn major_golf_pool.wsgi:application --bind 0.0.0.0:8000
