#!/bin/bash
set -e
echo "Deploy start"
cd /opt/Star-Burger
git pull
source env/bin/activate
pip install -r requirements.txt
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --publ>
python manage.py collectstatic --no-input
python manage.py migrate --no-input
systemctl restart  star-burger.service
systemctl reload nginx.service
commit=$(git rev-parse --short HEAD)
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --header 'X-Rollbar-Access-Token: 359bffe686014b2a8563ca47327f09d7' \
     --data '
{
