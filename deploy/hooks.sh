#!/bin/bash
echo "push"
git checkout deploy
git pull origin deploy
pip install -r requirements.txt 
python manage.py makemigrations
python manage.py migrate
#TODO: just for test now
#python manage.py runserver 0.0.0.0:8000