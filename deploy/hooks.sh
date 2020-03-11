#!/bin/bash
echo "push"
git checkout deploy
git pull origin deploy
pip install -r requirements.txt 
/ubuntu/home/yamigu_api_venv/bin/python manage.py makemigrations
/ubuntu/home/yamigu_api_venv/bin/python manage.py migrate
#TODO: just for test now
#python manage.py runserver 0.0.0.0:8000
