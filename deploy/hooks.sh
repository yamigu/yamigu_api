#!/bin/bash
echo "push"
git checkout deploy
git pull origin deploy
/home/ubuntu/yamigu_api_venv/bin/pip install -r requirements.txt 
/home/ubuntu/yamigu_api_venv/bin/python manage.py makemigrations
/home/ubuntu/yamigu_api_venv/bin/python manage.py migrate
#TODO: just for test now
#python manage.py runserver 0.0.0.0:8000
