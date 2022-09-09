#!/bin/bash
set -e
echo "Deploy start"
cd /opt/Star-Burger
git pull
source env/bin/activate
pip install -r requirements.txt
npm ci --dev
python manage.py collectstatic --no-input
python manage.py migrate
systemctl restart  star-burger.service
systemctl reload nginx.service
echo "Deploy was end success"
