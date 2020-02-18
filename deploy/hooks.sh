#!/bin/bash
echo "push"
git checkout -t origin/deploy
git pull origin deploy
#TODO: just for test now
python manage.py runserver 0.0.0.0:8000