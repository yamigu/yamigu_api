#!/bin/bash
echo "push"
git checkout -t origin/deploy
git pull origin deploy
python manage.py runserver 0.0.0.0:8000