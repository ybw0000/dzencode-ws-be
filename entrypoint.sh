#!/bin/bash

./wait-for-it.sh -h $POSTGRES_HOST -p $POSTGRES_PORT -t 0

python manage.py migrate

gunicorn -c gunicorn.conf.py core.asgi:application