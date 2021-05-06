python manage.py flush --no-input --settings atlas.settings.demo
python manage.py migrate --run-syncdb  --settings atlas.settings.demo
python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo
